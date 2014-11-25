#!/bin/bash -e
#
# Copyright 2009 João Miguel Neves <joao.neves@intraneia.com>
# Copyright 2008 Zuza Software Foundation
#
# This file is part of Translate.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

##########################################################################
# NOTE: Documentation regarding (the use of) this script can be found at #
# http://translate.sourceforge.net/wiki/toolkit/mozilla_l10n_scripts     #
##########################################################################

abs_start_time=$(date +%s)
start_time=$abs_start_time
opt_vc=""
opt_build_xpi=""
opt_compare_locales="yes"
opt_copyfiles="yes"
opt_verbose=""
opt_time=""

progress=none
errorlevel=traceback
export USECPO=0
hgverbosity="--quiet" # --verbose to make it noisy
gitverbosity="--quiet" # --verbose to make it noisy
pomigrate2verbosity="--quiet"
get_moz_enUS_verbosity=""
easy_install_verbosity="--quiet"


for option in $*
do
	if [ "${option##-*}" != "$option" ]; then
		case $option in
			--xpi)
				opt_build_xpi="yes"
			;;
			--vc)
				opt_vc="yes"
			;;
			--no-compare-locales)
				opt_compare_locales=""
			;;
			--no-copyfiles)
				opt_copyfiles=""
			;;
			--verbose)
				opt_verbose="yes"
				hgverbosity="--verbose"
				gitverbosity=""
				progress=bar
				pomigrate2verbosity=""
				get_moz_enUS_verbosity="-v"
				easy_install_verbosity="--verbose"
			;;
			--time)
				opt_time="yes"
			;;
			*) 
			echo "Unkown option: $option"
			exit
			;;
		esac
		shift
	else
		break
	fi
done

if [ $# -eq 0 ]; then
	HG_LANGS="ach af ak am cy en-ZA ff gd hi-IN hz ki lg ng nso ny sah son st-LS su sw tn ur ve wo xog zu"
	COUNT_LANGS=25
else
	HG_LANGS=$*
	COUNT_LANGS=$#
fi

for lang in $HG_LANGS
do
	if [ "$lang" == "templates" ]; then
		opt_vc="yes"
		break
	fi
done

function verbose() {
	if [ "$opt_verbose" -o "$opt_time" ]; then
		info_color=32 # Green
		time_color=34 # Blue
		end_time=$(date +%s)
		time_diff=$(($end_time - $start_time))
		echo -e "\033[${info_color}mINFO:\033[0m $1 [previous step \033[${time_color}m$time_diff sec\033[0m]"
		start_time=$end_time
	fi
}

# FIXME lets make this the execution directory
BUILD_DIR="$(pwd)"
MOZ_DIR="mozilla-aurora"
MOZCENTRAL_DIR="${BUILD_DIR}/${MOZ_DIR}"
L10N_DIR="${BUILD_DIR}/l10n"
PO_DIR="${BUILD_DIR}/po"
L10N_ENUS="${PO_DIR}/templates-en-US"
POT_DIR="${PO_DIR}/templates"
TOOLS_DIR="${BUILD_DIR}/tools"
# FIXME we should build this from the get_moz_enUS script
PRODUCT_DIRS="browser dom netwerk security services/sync toolkit mobile embedding" # Directories in language repositories to clear before running po2moz
# Directories in language repositories to clear before running po2moz
RETIRED_PRODUCT_DIRS="other-licenses/branding/firefox extensions/reporter"
LANGPACK_DIR="${BUILD_DIR}/xpi"

# Include current dir in path (for buildxpi and others)
CURDIR=$(dirname $0)
if [ "$CURDIR" == "" -o  "$CURDIR" == '.' ]; then
    CURDIR=$(pwd)
fi
PATH=${CURDIR}:${PATH}

if [ $opt_vc ]; then
	verbose "Translate Toolkit - update/pull using Git"
	if [ -d ${TOOLS_DIR}/translate/.git ]; then
		(cd ${TOOLS_DIR}/translate/
		git stash $gitverbosity
		git pull $gitverbosity --rebase
		git checkout $gitverbosity
		git stash pop $gitverbosity || true)
	else
		git clone $gitverbosity git@github.com:translate/translate.git ${TOOLS_DIR}/translate || git clone $gitverbosity git://github.com/translate/translate.git ${TOOLS_DIR}/translate
	fi
fi

if [ $opt_vc ]; then
	verbose "Compare-Locales - update if needed"
	easy_install $easy_install_verbosity --upgrade compare-locales
fi

export PYTHONPATH="${TOOLS_DIR}/translate":"$PYTHONPATH"
export PATH="${TOOLS_DIR}/translate/tools":\
"${TOOLS_DIR}/translate/translate/convert":\
"${TOOLS_DIR}/translate/translate/tools":\
"${TOOLS_DIR}/translate/translate/filters":\
"${TOOLS_DIR}/translate/tools/mozilla":\
"$PATH"

if [ $opt_vc ]; then
	verbose "${MOZ_DIR} - update/pull using Mercurial"
	if [ -d "${MOZCENTRAL_DIR}/.hg" ]; then
		cd ${MOZCENTRAL_DIR}
		hg pull $hgverbosity -u
		hg update $hgverbosity -C
	else
		hg clone $hgverbosity http://hg.mozilla.org/releases/${MOZ_DIR}/ ${MOZCENTRAL_DIR}
	fi
fi

if [ "$opt_vc" -o ! -d "${PO_DIR}" ]; then
	verbose "Translations - prepare the parent directory po/"
	for trans_repo in ${PO_DIR}
	do
		if [ -d $trans_repo ]; then
			(cd $trans_repo
			git stash $gitverbosity
			git pull $gitverbosity --rebase
			git checkout $gitverbosity
			git stash pop $gitverbosity || true)
		else
			git clone $gitverbosity git@github.com:translate/mozilla-l10n.git $trans_repo || git clone $gitverbosity git://github.com/translate/mozilla-l10n.git $trans_repo
		fi
	done
fi

verbose "Localisations - update Mercurial-managed languages in l10n/"
mkdir -p ${L10N_DIR}
cd ${L10N_DIR}
for lang in ${HG_LANGS}
do
	if [ $opt_vc ]; then
		verbose "Update l10n/$lang"
		if [ -d ${lang} ]; then
			if [ -d ${lang}/.hg ]; then
			        (cd ${lang}
				hg revert $hgverbosity --no-backup --all -r default
				hg pull $hgverbosity -u
				hg update $hgverbosity -C)
			else
			        rm -rf ${lang}/* 
			fi
		else
		    hg clone $hgverbosity http://hg.mozilla.org/releases/l10n/${MOZ_DIR}/${lang} ${lang} || mkdir ${lang}
		fi
	fi
done

if [ $opt_vc ]; then
	[ -d ${POT_DIR} ] && rm -rf ${POT_DIR}/
	
	verbose "Extract the en-US source files from the repo into localisation structure"
	rm -rf ${L10N_ENUS} ${PO_DIR}/en-US
	get_moz_enUS.py $get_moz_enUS_verbosity -s ../${MOZ_DIR} -d ${PO_DIR} -p browser
	get_moz_enUS.py $get_moz_enUS_verbosity -s ../${MOZ_DIR} -d ${PO_DIR} -p mobile
	mv ${PO_DIR}/en-US ${L10N_ENUS}
	
	verbose "moz2po - Create POT files from n-US"
	(cd ${L10N_ENUS}
	moz2po --errorlevel=$errorlevel --progress=$progress -P --duplicates=msgctxt --exclude '.hg'  . ${POT_DIR}
	)
	if [ $USECPO -eq 0 ]; then
		verbose "Cleanup - fix POT files using msgcat"
		(cd ${POT_DIR}
		for po in $(find ${PRODUCT_DIRS} -regex ".*\.po[t]?$")
		do
			msgcat -o $po.2 $po 2> >(egrep -v "warning: internationali[zs]ed messages should not contain the .* escape sequence" >&2) && mv $po.2 $po # parallel?
		done
		)
	fi
	pot_dir=$(basename ${POT_DIR})
	(cd ${POT_DIR}/..
	[ "$(git status --porcelain ${pot_dir})" != "?? ${pot_dir}/" ] && git checkout $gitverbosity -- $(git difftool -y -x 'diff --unified=3 --ignore-matching-lines=POT-Creation --ignore-matching-lines=X-Generator -s' ${pot_dir} |
	egrep "are identical$" |
	sed "s/^Files.*.\.pot and //;s/\(\.pot\).*/\1/") || echo "No header only changes, so no reverts needed"
	)
fi

# The following functions are used in the loop following it
function copyfile {
	filename=$1
	language=$2
	directory=$(dirname $filename)
	if [ -f ${L10N_ENUS}/$filename ]; then
		mkdir -p ${L10N_DIR}/$language/$directory
		cp -p ${L10N_ENUS}/$filename ${L10N_DIR}/$language/$directory
	fi
}

function copyfileifmissing {
	filename=$1
	language=$2
	if [ ! -f ${L10N_DIR}/$language/$filename ]; then
		copyfile $1 $2
	fi
}

function copyfiletype {
	filetype=$1
	language=$2
	files=$(cd ${L10N_ENUS}; find . -name "$filetype")
	for file in $files
	do
		copyfile $file $language
	done
}

function copydir {
	dir=$1
	language=$2
	if [ -d ${L10N_ENUS}/$dir ]; then
		files=$(cd ${L10N_ENUS}/$dir && find . -type f)
		for file in $files
		do
			copyfile $dir/$file $language
		done
	fi
}

verbose "Update ${PO_DIR} in case any changes are in version control"
(cd ${PO_DIR};
git stash $gitverbosity
git pull $gitverbosity --rebase
git checkout $gitverbosity
git stash pop $gitverbosity || true)

verbose "Translations - build l10n/ files"
for lang in ${HG_LANGS}
do
	if [ "$lang" == "templates" ]; then
		continue
	fi
	[ $COUNT_LANGS -gt 1 ] && echo "Language: $lang"
        polang=$(echo $lang|sed "s/-/_/g")
	verbose "Migrate - update PO files to new POT files"
	tempdir=`mktemp -d tmp.XXXXXXXXXX`
	if [ -d ${PO_DIR}/${polang} ]; then
		cp -R ${PO_DIR}/${polang} ${tempdir}/${polang}
		(cd ${PO_DIR}/${polang}; rm $(find ${PRODUCT_DIRS} ${RETIRED_PRODUCT_DIR} -type f -name "*.po"))
	fi
	pomigrate2 --use-compendium --pot2po $pomigrate2verbosity ${tempdir}/${polang} ${PO_DIR}/${polang} ${POT_DIR}
	rm -rf ${tempdir}

	(cd ${PO_DIR}
	if [ $USECPO -eq 0 ]; then
		verbose "Migration cleanup - fix migrated PO files using msgcat"
		(cd ${polang}
		for po in $(find ${PRODUCT_DIRS} -regex ".*\.po[t]?$")
		do
			msgcat -o $po.2 $po 2> >(egrep -v "warning: internationali[zs]ed messages should not contain the .* escape sequence" >&2) && mv $po.2 $po # parallel?
		done
		)
	fi

	verbose "Migration cleanup - Revert files with only header changes"
	[ "$(git status --porcelain ${polang})" != "?? ${polang}/" ] && git checkout $gitverbosity -- $(git difftool -y -x 'diff --unified=3 --ignore-matching-lines=POT-Creation --ignore-matching-lines=X-Generator -s' ${polang} |
	egrep "are identical$" |
	sed "s/^Files.*.\.po and //;s/\(\.po\).*/\1/") || echo "No header only changes, so no reverts needed"

	verbose "Migrate to new PO files: move old to obsolete/ and add new files"
	if [ "$(git status --porcelain ${polang})" == "?? ${polang}/" ]; then
		# Not VC managed, assume it's a new language
		git add ${polang}/\*.po
	else
		(cd ${polang}
		for newfile in $(git status --porcelain $PRODUCT_DIRS | egrep "^\?\?" | sed "s/^??\w*[^\/]*\///")
		do
			if [ -f $newfile -a "$(basename $newfile | cut -d"." -f3)" = "po" ]; then
				git add $newfile
			elif [ -d $newfile -a "$(find $newfiles -name '*.po')" ]; then
				git add $newfile
			fi
		done

		for oldfile in $(git status --porcelain $PRODUCT_DIRS $RETIRED_PRODUCT_DIRS | egrep "^ D" | sed "s/^ D\w*[^\/]*\///")
		do
			# FIXME - allow POT files also
			if [ "$(basename $oldfile | cut -d'.' -f3)" = "po" ]; then
				git checkout $gitverbosity -- $oldfile
				mkdir -p obsolete/$(dirname $oldfile)
				git mv $oldfile obsolete/$oldfile
			fi
		done
		# FIXME - do a PO cleanup here
		)
	fi
	)

	verbose "Pre-po2moz hacks"
	lang_product_dirs=
	for dir in ${PRODUCT_DIRS}; do lang_product_dirs="${lang_product_dirs} ${L10N_DIR}/$lang/$dir"; done
	for product_dir in ${lang_product_dirs}
	do
		[ -d ${product_dir} ] && find ${product_dir} \( -name '*.dtd' -o -name '*.properties' \) -exec rm -f {} \;
	done

	verbose "po2moz - Create Mozilla l10n layout from migrated PO files."
	for exclude in $RETIRED_PRODUCT_DIR
	do
		excludes=$(echo '$excludes --exclude="$exclude"')
	done
	echo $excludes
	po2moz --progress=$progress --errorlevel=$errorlevel --exclude=".git" --exclude=".hg" --exclude=".hgtags" --exclude="obsolete" --exclude="editor" --exclude="mail" --exclude="thunderbird" --exclude="chat" --exclude="*~" $excludes \
		-t ${L10N_ENUS} -i ${PO_DIR}/${polang} -o ${L10N_DIR}/${lang}

	if [ $opt_copyfiles ]; then
		verbose "Copy files not handled by moz2po/po2moz"
		copyfileifmissing toolkit/chrome/mozapps/help/welcome.xhtml ${lang}
		copyfileifmissing toolkit/chrome/mozapps/help/help-toc.rdf ${lang}
		copyfile browser/firefox-l10n.js ${lang}
		copyfile browser/profile/chrome/userChrome-example.css ${lang}
		copyfile browser/profile/chrome/userContent-example.css ${lang}
		copyfileifmissing toolkit/chrome/global/intl.css ${lang}
		# This one needs special approval but we need it to pass and compile
		copyfileifmissing browser/searchplugins/list.txt ${lang}
		# Revert some files that need careful human review or authorisation
		if [ -d ${L10N_DIR}/${lang}/.hg ]; then
			(cd ${L10N_DIR}/${lang}
			hg revert $hgverbosity --no-backup browser/chrome/browser-region/region.properties browser/searchplugins/list.txt
			)
		fi
	fi

	## CREATE XPI LANGPACK
	if [ $opt_build_xpi ]; then
		mkdir -p ${LANGPACK_DIR}
		verbose "Language Pack - create an XPI"
		buildxpi.py -d -L ${L10N_DIR} -s ${MOZCENTRAL_DIR} -o ${LANGPACK_DIR} ${lang}
	fi

	# COMPARE LOCALES
	if [ $opt_compare_locales ]; then
		verbose "Compare-Locales - to find errors"
		if [ -f ${MOZCENTRAL_DIR}/browser/locales/l10n.ini ]; then
			compare-locales ${MOZCENTRAL_DIR}/browser/locales/l10n.ini ${L10N_DIR} $lang
			compare-locales ${MOZCENTRAL_DIR}/mobile/locales/l10n.ini ${L10N_DIR} $lang
		else
			echo "Can't run compare-locales without ${MOZCENTRAL_DIR} checkout"
		fi
	fi

done

# Cleanup rubbish we seem to leave behind
rm -rf ${L10N_DIR}/tmp*
abs_end_time=$(date +%s)
total_time=$(($abs_end_time - $abs_start_time))
verbose "Total time $(date --date="@$total_time" +%M:%S)"
