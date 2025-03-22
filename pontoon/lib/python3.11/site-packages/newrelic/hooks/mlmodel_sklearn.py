# Copyright 2010 New Relic, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import sys
import uuid

from newrelic.api.function_trace import FunctionTrace
from newrelic.api.time_trace import current_trace
from newrelic.api.transaction import current_transaction
from newrelic.common.object_wrapper import ObjectProxy, wrap_function_wrapper
from newrelic.core.config import global_settings

METHODS_TO_WRAP = ("predict", "fit", "fit_predict", "predict_log_proba", "predict_proba", "transform", "score")
METRIC_SCORERS = (
    "accuracy_score",
    "balanced_accuracy_score",
    "f1_score",
    "precision_score",
    "recall_score",
    "roc_auc_score",
    "r2_score",
)
PY2 = sys.version_info[0] == 2
_logger = logging.getLogger(__name__)


def isnumeric(column):
    import numpy as np

    try:
        column.astype(np.float64)
        return [True] * len(column)
    except:
        pass
    return [False] * len(column)


class PredictReturnTypeProxy(ObjectProxy):
    def __init__(self, wrapped, model_name, training_step):
        super(ObjectProxy, self).__init__(wrapped)
        self._nr_model_name = model_name
        self._nr_training_step = training_step


def _wrap_method_trace(module, class_, method, name=None, group=None):
    def _nr_wrapper_method(wrapped, instance, args, kwargs):
        transaction = current_transaction()
        trace = current_trace()

        if transaction is None:
            return wrapped(*args, **kwargs)

        settings = transaction.settings if transaction.settings is not None else global_settings()

        if settings and not settings.machine_learning.enabled:
            return wrapped(*args, **kwargs)

        wrapped_attr_name = "_nr_wrapped_%s" % method

        # If the method has already been wrapped do not wrap it again. This happens
        # when one class inherits from another and they both implement the method.
        if getattr(trace, wrapped_attr_name, False):
            return wrapped(*args, **kwargs)

        trace = FunctionTrace(name=name, group=group, source=wrapped)

        try:
            # Set the _nr_wrapped attribute to denote that this method is being wrapped.
            setattr(trace, wrapped_attr_name, True)

            with trace:
                return_val = wrapped(*args, **kwargs)
        finally:
            # Set the _nr_wrapped attribute to denote that this method is no longer wrapped.
            setattr(trace, wrapped_attr_name, False)

        # If this is the fit method, increment the training_step counter.
        if method in ("fit", "fit_predict"):
            training_step = getattr(instance, "_nr_wrapped_training_step", -1)
            setattr(instance, "_nr_wrapped_training_step", training_step + 1)

        # If this is the predict method, wrap the return type in an nr type with
        # _nr_wrapped attrs that will attach model info to the data.
        if method in ("predict", "fit_predict"):
            training_step = getattr(instance, "_nr_wrapped_training_step", "Unknown")
            create_prediction_event(transaction, class_, instance, args, kwargs, return_val)
            return PredictReturnTypeProxy(return_val, model_name=class_, training_step=training_step)
        return return_val

    wrap_function_wrapper(module, "%s.%s" % (class_, method), _nr_wrapper_method)


def _calc_prediction_feature_stats(prediction_input, class_, feature_column_names, tags):
    import numpy as np

    # Drop any feature columns that are not numeric since we can't compute stats
    # on non-numeric columns.
    x = np.array(prediction_input)
    isnumeric_features = np.apply_along_axis(isnumeric, 0, x)
    numeric_features = x[isnumeric_features]

    # Drop any feature column names that are not numeric since we can't compute stats
    # on non-numeric columns.
    feature_column_names = feature_column_names[isnumeric_features[0]]

    # Only compute stats for features if we have any feature columns left after dropping
    # non-numeric columns.
    num_cols = len(feature_column_names)
    if num_cols > 0:
        # Boolean selection of numpy array values reshapes the array to a single
        # dimension so we have to reshape it back into a 2D array.
        features = np.reshape(numeric_features, (len(numeric_features) // num_cols, num_cols))
        features = features.astype(dtype=np.float64)

        _record_stats(features, feature_column_names, class_, "Feature", tags)


def _record_stats(data, column_names, class_, column_type, tags):
    import numpy as np

    mean = np.mean(data, axis=0)
    percentile25 = np.percentile(data, q=0.25, axis=0)
    percentile50 = np.percentile(data, q=0.50, axis=0)
    percentile75 = np.percentile(data, q=0.75, axis=0)
    standard_deviation = np.std(data, axis=0)
    _min = np.min(data, axis=0)
    _max = np.max(data, axis=0)
    _count = data.shape[0]

    transaction = current_transaction()

    # Currently record_metric only supports a subset of these stats so we have
    # to upload them one at a time instead of as a dictionary of stats per
    # feature column.
    for index, col_name in enumerate(column_names):
        metric_name = "MLModel/Sklearn/Named/%s/Predict/%s/%s" % (class_, column_type, col_name)

        transaction.record_dimensional_metrics(
            [
                ("%s/%s" % (metric_name, "Mean"), float(mean[index]), tags),
                ("%s/%s" % (metric_name, "Percentile25"), float(percentile25[index]), tags),
                ("%s/%s" % (metric_name, "Percentile50"), float(percentile50[index]), tags),
                ("%s/%s" % (metric_name, "Percentile75"), float(percentile75[index]), tags),
                ("%s/%s" % (metric_name, "StandardDeviation"), float(standard_deviation[index]), tags),
                ("%s/%s" % (metric_name, "Min"), float(_min[index]), tags),
                ("%s/%s" % (metric_name, "Max"), float(_max[index]), tags),
                ("%s/%s" % (metric_name, "Count"), _count, tags),
            ]
        )


def _calc_prediction_label_stats(labels, class_, label_column_names, tags):
    import numpy as np

    labels = np.array(labels, dtype=np.float64)
    _record_stats(labels, label_column_names, class_, "Label", tags)


def _get_label_names(user_defined_label_names, prediction_array):
    import numpy as np

    if user_defined_label_names is None:
        return np.array(range(prediction_array.shape[1]))
    if user_defined_label_names and len(user_defined_label_names) != prediction_array.shape[1]:
        _logger.warning(
            "The number of label names passed to the ml_model wrapper function is not equal to the number of predictions in the data set. Please supply the correct number of label names."
        )
        return np.array(range(prediction_array.shape[1]))
    else:
        return user_defined_label_names


def find_type_category(data_set, row_index, column_index):
    # If pandas DataFrame, return type of column.
    pd = sys.modules.get("pandas", None)
    if pd and isinstance(data_set, pd.DataFrame):
        value_type = data_set.iloc[:, column_index].dtype.name
        if value_type == "category":
            return "categorical"
        categorized_value_type = categorize_data_type(value_type)
        return categorized_value_type
    # If it's not a pandas DataFrame then it is a list or numpy array.
    python_type = str(type(data_set[column_index][row_index]))
    return categorize_data_type(python_type)


def categorize_data_type(python_type):
    if "int" in python_type or "float" in python_type or "complex" in python_type:
        return "numeric"
    if "bool" in python_type:
        return "bool"
    if "str" in python_type or "unicode" in python_type:
        return "str"
    else:
        return python_type


def _get_feature_column_names(user_provided_feature_names, features):
    import numpy as np

    num_feature_columns = np.array(features).shape[1]

    # If the user provided feature names are the correct size, return the user provided feature
    # names.
    if user_provided_feature_names and len(user_provided_feature_names) == num_feature_columns:
        return np.array(user_provided_feature_names)

    # If the user provided feature names aren't the correct size, log a warning and do not use the user provided feature names.
    if user_provided_feature_names:
        _logger.warning(
            "The number of feature names passed to the ml_model wrapper function is not equal to the number of columns in the data set. Please supply the correct number of feature names."
        )

    # If the user doesn't provide the feature names or they were provided but the size was incorrect and the features are a pandas data frame, return the column names from the pandas data frame.
    pd = sys.modules.get("pandas", None)
    if pd and isinstance(features, pd.DataFrame):
        return features.columns

    # If the user doesn't provide the feature names or they were provided but the size was incorrect and the features are not a pandas data frame, return the column indexes as the feature names.
    return np.array(range(num_feature_columns))


def bind_predict(X, *args, **kwargs):
    return X


def create_prediction_event(transaction, class_, instance, args, kwargs, return_val):
    import numpy as np

    data_set = bind_predict(*args, **kwargs)
    model_name = getattr(instance, "_nr_wrapped_name", class_)
    model_version = getattr(instance, "_nr_wrapped_version", "0.0.0")
    user_provided_feature_names = getattr(instance, "_nr_wrapped_feature_names", None)
    label_names = getattr(instance, "_nr_wrapped_label_names", None)
    metadata = getattr(instance, "_nr_wrapped_metadata", {})
    settings = transaction.settings if transaction.settings is not None else global_settings()

    prediction_id = uuid.uuid4()

    labels = []
    if return_val is not None:
        if not hasattr(return_val, "__iter__"):
            labels = np.array([return_val])
        else:
            labels = np.array(return_val)
        if len(labels.shape) == 1:
            labels = np.reshape(labels, (len(labels) // 1, 1))

        label_names_list = _get_label_names(label_names, labels)
        _calc_prediction_label_stats(
            labels,
            class_,
            label_names_list,
            tags={
                "prediction_id": prediction_id,
                "model_version": model_version,
                # The following are used for entity synthesis.
                "modelName": model_name,
            },
        )

    final_feature_names = _get_feature_column_names(user_provided_feature_names, data_set)
    np_casted_data_set = np.array(data_set)
    _calc_prediction_feature_stats(
        data_set,
        class_,
        final_feature_names,
        tags={
            "prediction_id": prediction_id,
            "model_version": model_version,
            # The following are used for entity synthesis.
            "modelName": model_name,
        },
    )
    features, predictions = np_casted_data_set.shape
    for prediction_index, prediction in enumerate(np_casted_data_set):
        inference_id = uuid.uuid4()

        event = {
            "inference_id": inference_id,
            "prediction_id": prediction_id,
            "model_version": model_version,
            "new_relic_data_schema_version": 2,
            # The following are used for entity synthesis.
            "modelName": model_name,
        }
        if metadata and isinstance(metadata, dict):
            event.update(metadata)
        # Don't include the raw value when inference_event_value is disabled.
        if settings and settings.machine_learning and settings.machine_learning.inference_events_value.enabled:
            event.update(
                {
                    "feature.%s" % str(final_feature_names[feature_col_index]): value
                    for feature_col_index, value in enumerate(prediction)
                }
            )
            event.update(
                {
                    "label.%s" % str(label_names_list[index]): str(value)
                    for index, value in enumerate(labels[prediction_index])
                }
            )
        transaction.record_ml_event("InferenceData", event)


def _nr_instrument_model(module, model_class):
    for method_name in METHODS_TO_WRAP:
        if hasattr(getattr(module, model_class), method_name):
            # Function/MLModel/Sklearn/Named/<class name>.<method name>
            name = "MLModel/Sklearn/Named/%s.%s" % (model_class, method_name)
            _wrap_method_trace(module, model_class, method_name, name=name)


def _instrument_sklearn_models(module, model_classes):
    for model_cls in model_classes:
        if hasattr(module, model_cls):
            _nr_instrument_model(module, model_cls)


def _bind_scorer(y_true, y_pred, *args, **kwargs):
    return y_true, y_pred, args, kwargs


def wrap_metric_scorer(wrapped, instance, args, kwargs):
    transaction = current_transaction()
    # If there is no transaction, do not wrap anything.
    if not transaction:
        return wrapped(*args, **kwargs)

    settings = transaction.settings if transaction.settings is not None else global_settings()

    if settings and not settings.machine_learning.enabled:
        return wrapped(*args, **kwargs)

    score = wrapped(*args, **kwargs)

    y_true, y_pred, args, kwargs = _bind_scorer(*args, **kwargs)
    model_name = "Unknown"
    training_step = "Unknown"
    if hasattr(y_pred, "_nr_model_name"):
        model_name = y_pred._nr_model_name
    if hasattr(y_pred, "_nr_training_step"):
        training_step = y_pred._nr_training_step
    # Attribute values must be int, float, str, or boolean. If it's not one of these
    # types and an iterable add the values as separate attributes.
    if not isinstance(score, (str, int, float, bool)):
        if hasattr(score, "__iter__"):
            for i, s in enumerate(score):
                transaction._add_agent_attribute(
                    "%s/TrainingStep/%s/%s[%s]" % (model_name, training_step, wrapped.__name__, i), s
                )
    else:
        transaction._add_agent_attribute("%s/TrainingStep/%s/%s" % (model_name, training_step, wrapped.__name__), score)
    return score


def instrument_sklearn_tree_models(module):
    model_classes = (
        "DecisionTreeClassifier",
        "DecisionTreeRegressor",
        "ExtraTreeClassifier",
        "ExtraTreeRegressor",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_ensemble_bagging_models(module):
    model_classes = (
        "BaggingClassifier",
        "BaggingRegressor",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_ensemble_forest_models(module):
    model_classes = (
        "ExtraTreesClassifier",
        "ExtraTreesRegressor",
        "RandomForestClassifier",
        "RandomForestRegressor",
        "RandomTreesEmbedding",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_ensemble_iforest_models(module):
    model_classes = ("IsolationForest",)
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_ensemble_weight_boosting_models(module):
    model_classes = (
        "AdaBoostClassifier",
        "AdaBoostRegressor",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_ensemble_gradient_boosting_models(module):
    model_classes = (
        "GradientBoostingClassifier",
        "GradientBoostingRegressor",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_ensemble_voting_models(module):
    model_classes = (
        "VotingClassifier",
        "VotingRegressor",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_ensemble_stacking_models(module):
    module_classes = (
        "StackingClassifier",
        "StackingRegressor",
    )
    _instrument_sklearn_models(module, module_classes)


def instrument_sklearn_ensemble_hist_models(module):
    model_classes = (
        "HistGradientBoostingClassifier",
        "HistGradientBoostingRegressor",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_linear_coordinate_descent_models(module):
    model_classes = (
        "Lasso",
        "LassoCV",
        "ElasticNet",
        "ElasticNetCV",
        "MultiTaskLasso",
        "MultiTaskLassoCV",
        "MultiTaskElasticNet",
        "MultiTaskElasticNetCV",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_compose_models(module):
    model_classes = (
        "ColumnTransformer",
        "TransformedTargetRegressor",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_covariance_shrunk_models(module):
    model_classes = (
        "ShrunkCovariance",
        "LedoitWolf",
        "OAS",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_cross_decomposition_models(module):
    model_classes = (
        "PLSRegression",
        "PLSSVD",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_covariance_graph_models(module):
    model_classes = (
        "GraphicalLasso",
        "GraphicalLassoCV",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_discriminant_analysis_models(module):
    model_classes = (
        "LinearDiscriminantAnalysis",
        "QuadraticDiscriminantAnalysis",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_covariance_models(module):
    model_classes = (
        "EmpiricalCovariance",
        "MinCovDet",
        "EllipticEnvelope",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_gaussian_process_models(module):
    model_classes = (
        "GaussianProcessClassifier",
        "GaussianProcessRegressor",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_dummy_models(module):
    model_classes = (
        "DummyClassifier",
        "DummyRegressor",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_feature_selection_rfe_models(module):
    model_classes = (
        "RFE",
        "RFECV",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_kernel_ridge_models(module):
    model_classes = ("KernelRidge",)
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_calibration_models(module):
    model_classes = ("CalibratedClassifierCV",)
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_cluster_models(module):
    model_classes = (
        "AffinityPropagation",
        "Birch",
        "DBSCAN",
        "MeanShift",
        "OPTICS",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_linear_least_angle_models(module):
    model_classes = (
        "Lars",
        "LarsCV",
        "LassoLars",
        "LassoLarsCV",
        "LassoLarsIC",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_feature_selection_models(module):
    model_classes = (
        "VarianceThreshold",
        "SelectFromModel",
        "SequentialFeatureSelector",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_cluster_agglomerative_models(module):
    model_classes = (
        "AgglomerativeClustering",
        "FeatureAgglomeration",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_linear_GLM_models(module):
    model_classes = (
        "PoissonRegressor",
        "GammaRegressor",
        "TweedieRegressor",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_cluster_clustering_models(module):
    model_classes = (
        "SpectralBiclustering",
        "SpectralCoclustering",
        "SpectralClustering",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_linear_stochastic_gradient_models(module):
    model_classes = (
        "SGDClassifier",
        "SGDRegressor",
        "SGDOneClassSVM",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_linear_ridge_models(module):
    model_classes = (
        "Ridge",
        "RidgeCV",
        "RidgeClassifier",
        "RidgeClassifierCV",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_linear_logistic_models(module):
    model_classes = (
        "LogisticRegression",
        "LogisticRegressionCV",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_linear_OMP_models(module):
    model_classes = (
        "OrthogonalMatchingPursuit",
        "OrthogonalMatchingPursuitCV",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_linear_passive_aggressive_models(module):
    model_classes = (
        "PassiveAggressiveClassifier",
        "PassiveAggressiveRegressor",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_linear_bayes_models(module):
    model_classes = (
        "ARDRegression",
        "BayesianRidge",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_linear_models(module):
    model_classes = (
        "HuberRegressor",
        "LinearRegression",
        "Perceptron",
        "QuantileRegressor",
        "TheilSenRegressor",
        "RANSACRegressor",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_cluster_kmeans_models(module):
    model_classes = (
        "BisectingKMeans",
        "KMeans",
        "MiniBatchKMeans",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_multiclass_models(module):
    model_classes = (
        "OneVsRestClassifier",
        "OneVsOneClassifier",
        "OutputCodeClassifier",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_multioutput_models(module):
    model_classes = (
        "MultiOutputEstimator",
        "MultiOutputClassifier",
        "ClassifierChain",
        "RegressorChain",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_naive_bayes_models(module):
    model_classes = (
        "GaussianNB",
        "MultinomialNB",
        "ComplementNB",
        "BernoulliNB",
        "CategoricalNB",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_model_selection_models(module):
    model_classes = (
        "GridSearchCV",
        "RandomizedSearchCV",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_mixture_models(module):
    model_classes = (
        "GaussianMixture",
        "BayesianGaussianMixture",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_neural_network_models(module):
    model_classes = (
        "BernoulliRBM",
        "MLPClassifier",
        "MLPRegressor",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_neighbors_KRadius_models(module):
    model_classes = (
        "KNeighborsClassifier",
        "RadiusNeighborsClassifier",
        "KNeighborsTransformer",
        "RadiusNeighborsTransformer",
        "KNeighborsRegressor",
        "RadiusNeighborsRegressor",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_svm_models(module):
    model_classes = (
        "LinearSVC",
        "LinearSVR",
        "SVC",
        "NuSVC",
        "SVR",
        "NuSVR",
        "OneClassSVM",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_semi_supervised_models(module):
    model_classes = (
        "LabelPropagation",
        "LabelSpreading",
        "SelfTrainingClassifier",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_pipeline_models(module):
    model_classes = (
        "Pipeline",
        "FeatureUnion",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_neighbors_models(module):
    model_classes = (
        "KernelDensity",
        "LocalOutlierFactor",
        "NeighborhoodComponentsAnalysis",
        "NearestCentroid",
        "NearestNeighbors",
    )
    _instrument_sklearn_models(module, model_classes)


def instrument_sklearn_metrics(module):
    for scorer in METRIC_SCORERS:
        if hasattr(module, scorer):
            wrap_function_wrapper(module, scorer, wrap_metric_scorer)
