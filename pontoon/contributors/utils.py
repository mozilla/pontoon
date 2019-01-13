def map_translations_to_events(days, translations):
    """
    Map translations into events (jsonable dictionaries) to display them on the user timeline.
    :param QuerySet[Translation] events: a QuerySet with translastions.
    :rtype: list[dict]
    :return: A list of dicts with mapped fields.
    """
    timeline = []
    for day in days:
        daily = translations.filter(date__startswith=day['day'])
        daily.prefetch_related('entity__resource__project')
        example = daily.order_by('-pk').first()

        timeline.append({
            'date': example.date,
            'type': 'translation',
            'count': day['count'],
            'project': example.entity.resource.project,
            'translation': example,
        })

    return timeline

