"""
MONJED Deterministic Emergency Action Localizer

Provides approved, deterministic translations for backend-approved
emergency actions used by the SMS communication layer.

IMPORTANT:
- Does NOT calculate or modify scientific risk.
- Does NOT modify operational decisions.
- Does NOT use generative AI.
- Unknown actions safely remain in their original English form.
- Translation is communication-only.
"""


SUPPORTED_LANGUAGES = {
    "en",
    "ar",
    "sw",
    "fr",
}


REQUIRED_TRANSLATION_LANGUAGES = {
    "ar",
    "sw",
    "fr",
}


# ============================================================
# APPROVED ACTION TRANSLATIONS
# ============================================================

# The exact English Decision Engine action is the lookup key.
# Only known, reviewed actions are translated.
#
# Safety rule:
# If the Decision Engine produces a new or unknown action,
# MONJED keeps the approved English text instead of inventing
# a translation.

ACTION_TRANSLATIONS: dict[str, dict[str, str]] = {

    # ========================================================
    # GENERIC FALLBACKS
    # ========================================================

    "Follow official safety guidance.": {
        "ar": "اتبع إرشادات السلامة الرسمية.",
        "sw": "Fuata mwongozo rasmi wa usalama.",
        "fr": "Suivez les consignes officielles de sécurité.",
    },

    "Follow local authority instructions.": {
        "ar": "اتبع تعليمات السلطات المحلية.",
        "sw": "Fuata maelekezo ya mamlaka za eneo lako.",
        "fr": "Suivez les instructions des autorités locales.",
    },

    # ========================================================
    # FLOOD — CRITICAL
    # ========================================================

    (
        "Move away from flood-prone and low-lying areas "
        "and relocate to a safer elevated location if it "
        "is safe to do so."
    ): {
        "ar": (
            "ابتعد عن المناطق المنخفضة والمعرضة للفيضانات، "
            "وانتقل إلى مكان مرتفع وأكثر أمانًا إذا كان الانتقال آمنًا."
        ),
        "sw": (
            "Ondoka kwenye maeneo ya chini na yanayokumbwa na mafuriko, "
            "na uhamie sehemu ya juu na salama zaidi ikiwa ni salama kufanya hivyo."
        ),
        "fr": (
            "Éloignez-vous des zones basses et exposées aux inondations, "
            "et rejoignez un endroit plus sûr et en hauteur si vous pouvez "
            "le faire sans danger."
        ),
    },

    (
        "If safe movement is not possible, remain in the "
        "safest available elevated location and request "
        "official assistance."
    ): {
        "ar": (
            "إذا لم يكن الانتقال آمنًا، فابقَ في أكثر مكان مرتفع وآمن متاح "
            "واطلب المساعدة الرسمية."
        ),
        "sw": (
            "Ikiwa kuhama si salama, baki katika sehemu ya juu na salama zaidi "
            "inayopatikana na uombe msaada rasmi."
        ),
        "fr": (
            "Si vous ne pouvez pas vous déplacer sans danger, restez dans "
            "l'endroit en hauteur le plus sûr disponible et demandez une "
            "assistance officielle."
        ),
    },

    # ========================================================
    # FLOOD — HIGH
    # ========================================================

    (
        "Avoid low-lying areas and floodwater, monitor "
        "official warnings, and prepare to move to a safer "
        "elevated location."
    ): {
        "ar": (
            "تجنب المناطق المنخفضة ومياه الفيضانات، وتابع التحذيرات الرسمية، "
            "واستعد للانتقال إلى مكان مرتفع وأكثر أمانًا."
        ),
        "sw": (
            "Epuka maeneo ya chini na maji ya mafuriko, fuatilia tahadhari rasmi, "
            "na jiandae kuhamia sehemu ya juu na salama zaidi."
        ),
        "fr": (
            "Évitez les zones basses et les eaux de crue, suivez les alertes "
            "officielles et préparez-vous à rejoindre un endroit plus sûr et "
            "en hauteur."
        ),
    },

    (
        "If conditions worsen or access becomes unsafe, "
        "move to the safest available elevated location "
        "and request assistance if needed."
    ): {
        "ar": (
            "إذا ساءت الظروف أو أصبح الوصول غير آمن، فانتقل إلى أكثر مكان مرتفع "
            "وآمن متاح واطلب المساعدة عند الحاجة."
        ),
        "sw": (
            "Ikiwa hali itazidi kuwa mbaya au njia za kufikia zitakuwa si salama, "
            "hamia sehemu ya juu na salama zaidi inayopatikana na uombe msaada "
            "inapohitajika."
        ),
        "fr": (
            "Si les conditions s'aggravent ou si l'accès devient dangereux, "
            "rejoignez l'endroit en hauteur le plus sûr disponible et demandez "
            "de l'aide si nécessaire."
        ),
    },

    # ========================================================
    # FLOOD — MODERATE
    # ========================================================

    (
        "Monitor official flood guidance and avoid "
        "low-lying or flood-prone areas."
    ): {
        "ar": (
            "تابع إرشادات الفيضانات الرسمية وتجنب المناطق المنخفضة أو المعرضة "
            "للفيضانات."
        ),
        "sw": (
            "Fuatilia mwongozo rasmi kuhusu mafuriko na epuka maeneo ya chini "
            "au yanayokumbwa na mafuriko."
        ),
        "fr": (
            "Suivez les consignes officielles concernant les inondations et "
            "évitez les zones basses ou inondables."
        ),
    },

    (
        "Be prepared to move to a safer elevated location "
        "if warnings or local conditions worsen."
    ): {
        "ar": (
            "كن مستعدًا للانتقال إلى مكان مرتفع وأكثر أمانًا إذا ساءت التحذيرات "
            "أو الظروف المحلية."
        ),
        "sw": (
            "Kuwa tayari kuhamia sehemu ya juu na salama zaidi ikiwa tahadhari "
            "au hali za eneo zitazidi kuwa mbaya."
        ),
        "fr": (
            "Préparez-vous à rejoindre un endroit plus sûr et en hauteur si les "
            "alertes ou les conditions locales s'aggravent."
        ),
    },

    # ========================================================
    # FLOOD — LOW
    # ========================================================

    (
        "Continue monitoring official flood information "
        "and remain aware of changing local conditions."
    ): {
        "ar": (
            "استمر في متابعة المعلومات الرسمية عن الفيضانات وانتبه إلى تغير "
            "الظروف المحلية."
        ),
        "sw": (
            "Endelea kufuatilia taarifa rasmi kuhusu mafuriko na uwe makini na "
            "mabadiliko ya hali za eneo."
        ),
        "fr": (
            "Continuez à suivre les informations officielles sur les inondations "
            "et restez attentif à l'évolution des conditions locales."
        ),
    },

    (
        "Avoid floodwater and follow official guidance "
        "if conditions begin to worsen."
    ): {
        "ar": (
            "تجنب مياه الفيضانات واتبع الإرشادات الرسمية إذا بدأت الظروف في "
            "التدهور."
        ),
        "sw": (
            "Epuka maji ya mafuriko na fuata mwongozo rasmi ikiwa hali itaanza "
            "kuwa mbaya."
        ),
        "fr": (
            "Évitez les eaux de crue et suivez les consignes officielles si les "
            "conditions commencent à se dégrader."
        ),
    },

    # ========================================================
    # PEOPLE TRAPPED — HUMAN REVIEW
    # ========================================================

    (
        "Request emergency or trained human assistance "
        "for the reported situation."
    ): {
        "ar": (
            "اطلب مساعدة طارئة أو مساعدة من شخص مدرَّب للتعامل مع الحالة "
            "المُبلغ عنها."
        ),
        "sw": (
            "Omba msaada wa dharura au msaada wa mtu aliyefunzwa kwa hali "
            "iliyoripotiwa."
        ),
        "fr": (
            "Demandez l'aide des services d'urgence ou d'une personne formée "
            "pour la situation signalée."
        ),
    },

    (
        "Do not attempt unsafe rescue actions. Share the "
        "location and available details with responders."
    ): {
        "ar": (
            "لا تحاول القيام بعملية إنقاذ غير آمنة. شارك الموقع والتفاصيل "
            "المتاحة مع فرق الاستجابة."
        ),
        "sw": (
            "Usijaribu kufanya uokoaji usio salama. Shiriki eneo na maelezo "
            "yanayopatikana na wahudumu wa dharura."
        ),
        "fr": (
            "Ne tentez pas d'opération de sauvetage dangereuse. Communiquez "
            "l'emplacement et les informations disponibles aux intervenants."
        ),
    },

    # ========================================================
    # FLOOD — STRUCTURAL DAMAGE + BLOCKED ROUTE + RISING WATER
    # ========================================================

    (
        "Stay away from visibly damaged buildings or "
        "infrastructure, avoid floodwater, and do not "
        "use routes reported as blocked or flooded. "
        "Move toward a safer elevated location only "
        "if a safe route is available."
    ): {
        "ar": (
            "ابتعد عن المباني أو البنية التحتية المتضررة بوضوح، وتجنب مياه "
            "الفيضانات، ولا تستخدم الطرق المُبلغ عن انسدادها أو غمرها بالمياه. "
            "انتقل إلى مكان مرتفع وأكثر أمانًا فقط إذا كان هناك طريق آمن."
        ),
        "sw": (
            "Kaa mbali na majengo au miundombinu iliyoharibika kwa wazi, epuka "
            "maji ya mafuriko, na usitumie njia zilizoripotiwa kuwa zimefungwa "
            "au zimefurika. Hamia sehemu ya juu na salama zaidi tu ikiwa kuna "
            "njia salama."
        ),
        "fr": (
            "Éloignez-vous des bâtiments ou infrastructures visiblement endommagés, "
            "évitez les eaux de crue et n'empruntez pas les routes signalées comme "
            "bloquées ou inondées. Rejoignez un endroit plus sûr et en hauteur "
            "uniquement si un itinéraire sûr est disponible."
        ),
    },

    (
        "If no safe route is confirmed, remain in the "
        "safest available elevated location away from "
        "visible structural hazards and request "
        "official assistance."
    ): {
        "ar": (
            "إذا لم يتم تأكيد طريق آمن، فابقَ في أكثر مكان مرتفع وآمن متاح، "
            "بعيدًا عن المخاطر الإنشائية الظاهرة، واطلب المساعدة الرسمية."
        ),
        "sw": (
            "Ikiwa hakuna njia salama iliyothibitishwa, baki katika sehemu ya juu "
            "na salama zaidi inayopatikana, mbali na hatari za miundo zinazoonekana, "
            "na uombe msaada rasmi."
        ),
        "fr": (
            "Si aucun itinéraire sûr n'est confirmé, restez dans l'endroit en "
            "hauteur le plus sûr disponible, loin des dangers structurels visibles, "
            "et demandez une assistance officielle."
        ),
    },

    # ========================================================
    # FLOOD — STRUCTURAL DAMAGE + BLOCKED ROUTE
    # ========================================================

    (
        "Stay away from visibly damaged buildings or "
        "infrastructure and do not use routes reported "
        "as blocked or flooded."
    ): {
        "ar": (
            "ابتعد عن المباني أو البنية التحتية المتضررة بوضوح، ولا تستخدم "
            "الطرق المُبلغ عن انسدادها أو غمرها بالمياه."
        ),
        "sw": (
            "Kaa mbali na majengo au miundombinu iliyoharibika kwa wazi na "
            "usitumie njia zilizoripotiwa kuwa zimefungwa au zimefurika."
        ),
        "fr": (
            "Éloignez-vous des bâtiments ou infrastructures visiblement endommagés "
            "et n'empruntez pas les routes signalées comme bloquées ou inondées."
        ),
    },

    (
        "Remain in the safest available location until "
        "a safer route is confirmed, and request "
        "official assistance if needed."
    ): {
        "ar": (
            "ابقَ في أكثر مكان آمن متاح حتى يتم تأكيد طريق أكثر أمانًا، واطلب "
            "المساعدة الرسمية عند الحاجة."
        ),
        "sw": (
            "Baki katika sehemu salama zaidi inayopatikana hadi njia salama zaidi "
            "ithibitishwe, na uombe msaada rasmi inapohitajika."
        ),
        "fr": (
            "Restez dans l'endroit le plus sûr disponible jusqu'à ce qu'un "
            "itinéraire plus sûr soit confirmé, et demandez une assistance "
            "officielle si nécessaire."
        ),
    },

    # ========================================================
    # FLOOD — STRUCTURAL DAMAGE + RISING WATER
    # ========================================================

    (
        "Stay away from visibly damaged buildings or "
        "infrastructure, avoid floodwater, and move away "
        "from areas where water levels are rising."
    ): {
        "ar": (
            "ابتعد عن المباني أو البنية التحتية المتضررة بوضوح، وتجنب مياه "
            "الفيضانات، وابتعد عن المناطق التي ترتفع فيها مستويات المياه."
        ),
        "sw": (
            "Kaa mbali na majengo au miundombinu iliyoharibika kwa wazi, epuka "
            "maji ya mafuriko, na ondoka kwenye maeneo ambako kiwango cha maji "
            "kinaongezeka."
        ),
        "fr": (
            "Éloignez-vous des bâtiments ou infrastructures visiblement endommagés, "
            "évitez les eaux de crue et éloignez-vous des zones où le niveau de "
            "l'eau monte."
        ),
    },

    (
        "If safe movement is not possible, remain in "
        "the safest available elevated location away "
        "from visible structural hazards and request "
        "official assistance."
    ): {
        "ar": (
            "إذا لم يكن الانتقال آمنًا، فابقَ في أكثر مكان مرتفع وآمن متاح، "
            "بعيدًا عن المخاطر الإنشائية الظاهرة، واطلب المساعدة الرسمية."
        ),
        "sw": (
            "Ikiwa kuhama si salama, baki katika sehemu ya juu na salama zaidi "
            "inayopatikana, mbali na hatari za miundo zinazoonekana, na uombe "
            "msaada rasmi."
        ),
        "fr": (
            "Si vous ne pouvez pas vous déplacer sans danger, restez dans "
            "l'endroit en hauteur le plus sûr disponible, loin des dangers "
            "structurels visibles, et demandez une assistance officielle."
        ),
    },

    # ========================================================
    # FLOOD — STRUCTURAL DAMAGE
    # ========================================================

    (
        "Stay away from visibly damaged buildings or "
        "infrastructure and avoid nearby floodwater."
    ): {
        "ar": (
            "ابتعد عن المباني أو البنية التحتية المتضررة بوضوح، وتجنب مياه "
            "الفيضانات القريبة."
        ),
        "sw": (
            "Kaa mbali na majengo au miundombinu iliyoharibika kwa wazi na "
            "epuka maji ya mafuriko yaliyo karibu."
        ),
        "fr": (
            "Éloignez-vous des bâtiments ou infrastructures visiblement endommagés "
            "et évitez les eaux de crue à proximité."
        ),
    },

    (
        "Move to a safer location if it is safe to do "
        "so. If safe movement is not possible, remain "
        "in the safest available location and request "
        "official assistance."
    ): {
        "ar": (
            "انتقل إلى مكان أكثر أمانًا إذا كان ذلك آمنًا. إذا لم يكن الانتقال "
            "آمنًا، فابقَ في أكثر مكان آمن متاح واطلب المساعدة الرسمية."
        ),
        "sw": (
            "Hamia sehemu salama zaidi ikiwa ni salama kufanya hivyo. Ikiwa "
            "kuhama si salama, baki katika sehemu salama zaidi inayopatikana "
            "na uombe msaada rasmi."
        ),
        "fr": (
            "Rejoignez un endroit plus sûr si vous pouvez le faire sans danger. "
            "Si vous ne pouvez pas vous déplacer sans danger, restez dans "
            "l'endroit le plus sûr disponible et demandez une assistance officielle."
        ),
    },

    # ========================================================
    # FLOOD — BLOCKED ROUTE + RISING WATER
    # ========================================================

    (
        "Avoid floodwater and do not use routes "
        "reported as blocked or flooded. Move away "
        "from areas where water levels are rising."
    ): {
        "ar": (
            "تجنب مياه الفيضانات ولا تستخدم الطرق المُبلغ عن انسدادها أو غمرها "
            "بالمياه. ابتعد عن المناطق التي ترتفع فيها مستويات المياه."
        ),
        "sw": (
            "Epuka maji ya mafuriko na usitumie njia zilizoripotiwa kuwa zimefungwa "
            "au zimefurika. Ondoka kwenye maeneo ambako kiwango cha maji kinaongezeka."
        ),
        "fr": (
            "Évitez les eaux de crue et n'empruntez pas les routes signalées comme "
            "bloquées ou inondées. Éloignez-vous des zones où le niveau de l'eau monte."
        ),
    },

    (
        "If no safe route is confirmed, remain in "
        "the safest available elevated location and "
        "request official assistance."
    ): {
        "ar": (
            "إذا لم يتم تأكيد طريق آمن، فابقَ في أكثر مكان مرتفع وآمن متاح "
            "واطلب المساعدة الرسمية."
        ),
        "sw": (
            "Ikiwa hakuna njia salama iliyothibitishwa, baki katika sehemu ya juu "
            "na salama zaidi inayopatikana na uombe msaada rasmi."
        ),
        "fr": (
            "Si aucun itinéraire sûr n'est confirmé, restez dans l'endroit en "
            "hauteur le plus sûr disponible et demandez une assistance officielle."
        ),
    },

    # ========================================================
    # FLOOD — BLOCKED ROUTE
    # ========================================================

    (
        "Do not use routes reported as blocked or "
        "flooded. Follow verified official guidance "
        "for a safer alternative."
    ): {
        "ar": (
            "لا تستخدم الطرق المُبلغ عن انسدادها أو غمرها بالمياه. اتبع الإرشادات "
            "الرسمية الموثوقة لاختيار طريق بديل أكثر أمانًا."
        ),
        "sw": (
            "Usitumie njia zilizoripotiwa kuwa zimefungwa au zimefurika. Fuata "
            "mwongozo rasmi uliothibitishwa ili kupata njia mbadala iliyo salama zaidi."
        ),
        "fr": (
            "N'empruntez pas les routes signalées comme bloquées ou inondées. "
            "Suivez les consignes officielles vérifiées pour trouver un itinéraire "
            "alternatif plus sûr."
        ),
    },

    (
        "If no safe route is confirmed, remain in "
        "the safest available location and request "
        "assistance."
    ): {
        "ar": (
            "إذا لم يتم تأكيد طريق آمن، فابقَ في أكثر مكان آمن متاح واطلب المساعدة."
        ),
        "sw": (
            "Ikiwa hakuna njia salama iliyothibitishwa, baki katika sehemu salama "
            "zaidi inayopatikana na uombe msaada."
        ),
        "fr": (
            "Si aucun itinéraire sûr n'est confirmé, restez dans l'endroit le plus "
            "sûr disponible et demandez de l'aide."
        ),
    },

    # ========================================================
    # FLOOD — RISING WATER
    # ========================================================

    (
        "Avoid floodwater and move away from areas "
        "where water levels are rising."
    ): {
        "ar": (
            "تجنب مياه الفيضانات وابتعد عن المناطق التي ترتفع فيها مستويات المياه."
        ),
        "sw": (
            "Epuka maji ya mafuriko na ondoka kwenye maeneo ambako kiwango cha "
            "maji kinaongezeka."
        ),
        "fr": (
            "Évitez les eaux de crue et éloignez-vous des zones où le niveau de "
            "l'eau monte."
        ),
    },

    (
        "If movement is unsafe, remain in the safest "
        "available elevated location and request "
        "assistance."
    ): {
        "ar": (
            "إذا كان الانتقال غير آمن، فابقَ في أكثر مكان مرتفع وآمن متاح "
            "واطلب المساعدة."
        ),
        "sw": (
            "Ikiwa kuhama si salama, baki katika sehemu ya juu na salama zaidi "
            "inayopatikana na uombe msaada."
        ),
        "fr": (
            "Si vous ne pouvez pas vous déplacer sans danger, restez dans "
            "l'endroit en hauteur le plus sûr disponible et demandez de l'aide."
        ),
    },

    # ========================================================
    # EARTHQUAKE — CRITICAL
    # ========================================================

    (
        "Stay away from visibly damaged buildings, "
        "unstable structures, and falling hazards. If you "
        "are inside a damaged building and can leave safely, "
        "move outside and away from it."
    ): {
        "ar": (
            "ابتعد عن المباني المتضررة بوضوح والمنشآت غير المستقرة ومصادر السقوط. "
            "إذا كنت داخل مبنى متضرر ويمكنك الخروج بأمان، فاخرج وابتعد عنه."
        ),
        "sw": (
            "Kaa mbali na majengo yaliyoharibika kwa wazi, miundo isiyo imara, "
            "na vitu vinavyoweza kuanguka. Ikiwa uko ndani ya jengo lililoharibika "
            "na unaweza kutoka kwa usalama, toka nje na uende mbali nalo."
        ),
        "fr": (
            "Éloignez-vous des bâtiments visiblement endommagés, des structures "
            "instables et des objets susceptibles de tomber. Si vous êtes dans "
            "un bâtiment endommagé et pouvez sortir sans danger, sortez et "
            "éloignez-vous-en."
        ),
    },

    (
        "Do not re-enter damaged buildings. Be ready for "
        "aftershocks; if shaking starts again, Drop, Cover, "
        "and Hold On."
    ): {
        "ar": (
            "لا تدخل المباني المتضررة مرة أخرى. كن مستعدًا للهزات الارتدادية؛ "
            "إذا بدأ الاهتزاز من جديد، انخفض إلى الأرض، احتمِ، وتمسّك."
        ),
        "sw": (
            "Usiingie tena kwenye majengo yaliyoharibika. Kuwa tayari kwa mitetemeko "
            "ya baadae; mtikisiko ukianza tena, jishushe chini, jisitiri, na ushikilie."
        ),
        "fr": (
            "Ne rentrez pas de nouveau dans les bâtiments endommagés. Préparez-vous "
            "aux répliques; si les secousses reprennent, baissez-vous, mettez-vous "
            "à l'abri et agrippez-vous."
        ),
    },

    # ========================================================
    # EARTHQUAKE — HIGH
    # ========================================================

    (
        "Move away from visibly damaged buildings, "
        "unstable structures, and other falling hazards "
        "if it is safe to do so."
    ): {
        "ar": (
            "ابتعد عن المباني المتضررة بوضوح والمنشآت غير المستقرة ومصادر السقوط "
            "الأخرى إذا كان ذلك آمنًا."
        ),
        "sw": (
            "Ondoka karibu na majengo yaliyoharibika kwa wazi, miundo isiyo imara, "
            "na hatari nyingine za vitu vinavyoweza kuanguka ikiwa ni salama kufanya hivyo."
        ),
        "fr": (
            "Éloignez-vous des bâtiments visiblement endommagés, des structures "
            "instables et des autres risques de chute si vous pouvez le faire "
            "sans danger."
        ),
    },

    (
        "Do not enter damaged structures. Be ready for "
        "aftershocks; if shaking starts again, Drop, Cover, "
        "and Hold On."
    ): {
        "ar": (
            "لا تدخل المنشآت المتضررة. كن مستعدًا للهزات الارتدادية؛ إذا بدأ "
            "الاهتزاز من جديد، انخفض إلى الأرض، احتمِ، وتمسّك."
        ),
        "sw": (
            "Usiingie kwenye miundo iliyoharibika. Kuwa tayari kwa mitetemeko ya "
            "baadae; mtikisiko ukianza tena, jishushe chini, jisitiri, na ushikilie."
        ),
        "fr": (
            "N'entrez pas dans les structures endommagées. Préparez-vous aux "
            "répliques; si les secousses reprennent, baissez-vous, mettez-vous "
            "à l'abri et agrippez-vous."
        ),
    },

    # ========================================================
    # EARTHQUAKE — MODERATE
    # ========================================================

    (
        "Stay away from visibly damaged structures, "
        "broken glass, and other nearby hazards."
    ): {
        "ar": (
            "ابتعد عن المنشآت المتضررة بوضوح والزجاج المكسور وأي مخاطر قريبة أخرى."
        ),
        "sw": (
            "Kaa mbali na miundo iliyoharibika kwa wazi, vioo vilivyovunjika, "
            "na hatari nyingine zilizo karibu."
        ),
        "fr": (
            "Éloignez-vous des structures visiblement endommagées, du verre brisé "
            "et des autres dangers à proximité."
        ),
    },

    (
        "Be alert for aftershocks. If shaking starts again, "
        "Drop, Cover, and Hold On."
    ): {
        "ar": (
            "انتبه للهزات الارتدادية. إذا بدأ الاهتزاز من جديد، انخفض إلى الأرض، "
            "احتمِ، وتمسّك."
        ),
        "sw": (
            "Kuwa makini na mitetemeko ya baadae. Mtikisiko ukianza tena, jishushe "
            "chini, jisitiri, na ushikilie."
        ),
        "fr": (
            "Restez attentif aux répliques. Si les secousses reprennent, baissez-vous, "
            "mettez-vous à l'abri et agrippez-vous."
        ),
    },

    # ========================================================
    # EARTHQUAKE — LOW
    # ========================================================

    (
        "Check your immediate surroundings for damage or "
        "falling hazards and stay away from any structure "
        "that appears unsafe."
    ): {
        "ar": (
            "افحص محيطك القريب بحثًا عن أضرار أو أشياء قد تسقط، وابتعد عن أي منشأة "
            "تبدو غير آمنة."
        ),
        "sw": (
            "Kagua mazingira yako ya karibu kwa uharibifu au vitu vinavyoweza "
            "kuanguka, na kaa mbali na muundo wowote unaoonekana kuwa si salama."
        ),
        "fr": (
            "Vérifiez les alentours immédiats pour repérer les dommages ou les objets "
            "susceptibles de tomber, et éloignez-vous de toute structure qui semble "
            "dangereuse."
        ),
    },

    # ========================================================
    # EARTHQUAKE — STRUCTURAL DAMAGE + BLOCKED ROUTE
    # ========================================================

    (
        "Stay away from damaged structures and do not "
        "use routes reported as blocked or unsafe."
    ): {
        "ar": (
            "ابتعد عن المنشآت المتضررة ولا تستخدم الطرق المُبلغ عن انسدادها أو "
            "عدم أمانها."
        ),
        "sw": (
            "Kaa mbali na miundo iliyoharibika na usitumie njia zilizoripotiwa "
            "kuwa zimefungwa au si salama."
        ),
        "fr": (
            "Éloignez-vous des structures endommagées et n'empruntez pas les routes "
            "signalées comme bloquées ou dangereuses."
        ),
    },

    (
        "Remain in the safest accessible location if "
        "you cannot leave safely. Wait for a confirmed "
        "safe route or trained assistance. If shaking "
        "starts again, Drop, Cover, and Hold On."
    ): {
        "ar": (
            "إذا لم تتمكن من المغادرة بأمان، فابقَ في أكثر مكان آمن يمكن الوصول إليه. "
            "انتظر تأكيد طريق آمن أو وصول مساعدة مدرَّبة. إذا بدأ الاهتزاز من جديد، "
            "انخفض إلى الأرض، احتمِ، وتمسّك."
        ),
        "sw": (
            "Ikiwa huwezi kuondoka kwa usalama, baki katika sehemu salama zaidi "
            "inayoweza kufikiwa. Subiri njia salama iliyothibitishwa au msaada wa "
            "watu waliofunzwa. Mtikisiko ukianza tena, jishushe chini, jisitiri, "
            "na ushikilie."
        ),
        "fr": (
            "Si vous ne pouvez pas partir sans danger, restez dans l'endroit "
            "accessible le plus sûr. Attendez qu'un itinéraire sûr soit confirmé "
            "ou qu'une aide formée arrive. Si les secousses reprennent, baissez-vous, "
            "mettez-vous à l'abri et agrippez-vous."
        ),
    },

    # ========================================================
    # EARTHQUAKE — STRUCTURAL DAMAGE
    # ========================================================

    (
        "Move away from visibly damaged structures "
        "and falling hazards if it is safe to do so."
    ): {
        "ar": (
            "ابتعد عن المنشآت المتضررة بوضوح ومصادر السقوط إذا كان ذلك آمنًا."
        ),
        "sw": (
            "Ondoka karibu na miundo iliyoharibika kwa wazi na hatari za vitu "
            "vinavyoweza kuanguka ikiwa ni salama kufanya hivyo."
        ),
        "fr": (
            "Éloignez-vous des structures visiblement endommagées et des risques "
            "de chute si vous pouvez le faire sans danger."
        ),
    },

    (
        "Do not re-enter damaged buildings. If shaking "
        "starts again, Drop, Cover, and Hold On."
    ): {
        "ar": (
            "لا تدخل المباني المتضررة مرة أخرى. إذا بدأ الاهتزاز من جديد، انخفض "
            "إلى الأرض، احتمِ، وتمسّك."
        ),
        "sw": (
            "Usiingie tena kwenye majengo yaliyoharibika. Mtikisiko ukianza tena, "
            "jishushe chini, jisitiri, na ushikilie."
        ),
        "fr": (
            "Ne rentrez pas de nouveau dans les bâtiments endommagés. Si les "
            "secousses reprennent, baissez-vous, mettez-vous à l'abri et agrippez-vous."
        ),
    },

    # ========================================================
    # EARTHQUAKE — BLOCKED ROUTE
    # ========================================================

    (
        "Do not use routes reported as blocked or "
        "unsafe. Remain on a confirmed safe route "
        "or in a safe location."
    ): {
        "ar": (
            "لا تستخدم الطرق المُبلغ عن انسدادها أو عدم أمانها. ابقَ على طريق تم "
            "تأكيد أمانه أو في مكان آمن."
        ),
        "sw": (
            "Usitumie njia zilizoripotiwa kuwa zimefungwa au si salama. Baki kwenye "
            "njia iliyothibitishwa kuwa salama au katika sehemu salama."
        ),
        "fr": (
            "N'empruntez pas les routes signalées comme bloquées ou dangereuses. "
            "Restez sur un itinéraire dont la sécurité est confirmée ou dans un "
            "endroit sûr."
        ),
    },

    (
        "Wait for a safer route or trained assistance "
        "rather than crossing blocked or visibly "
        "unsafe areas."
    ): {
        "ar": (
            "انتظر طريقًا أكثر أمانًا أو مساعدة مدرَّبة بدلًا من عبور مناطق مغلقة "
            "أو تبدو غير آمنة."
        ),
        "sw": (
            "Subiri njia salama zaidi au msaada wa watu waliofunzwa badala ya "
            "kuvuka maeneo yaliyofungwa au yanayoonekana kuwa si salama."
        ),
        "fr": (
            "Attendez un itinéraire plus sûr ou une assistance formée plutôt que "
            "de traverser des zones bloquées ou visiblement dangereuses."
        ),
    },
}

# ============================================================
# UPDATED FLOOD ACTIONS
#
# These entries match the current Decision Engine exactly.
# They replace older flood wording that relied too heavily
# on generic monitoring / guidance instructions.
# ============================================================

ACTION_TRANSLATIONS.update(
    {

        # ====================================================
        # FLOOD — CRITICAL BACKUP
        # ====================================================

        (
            "Do not walk or drive through floodwater. If safe "
            "movement is not possible, remain in the safest "
            "available elevated location and request assistance."
        ): {
            "ar": (
                "لا تمشِ أو تقد السيارة عبر مياه الفيضانات. "
                "إذا لم يكن الانتقال آمنًا، فابقَ في أكثر مكان "
                "مرتفع وآمن متاح واطلب المساعدة."
            ),
            "sw": (
                "Usitembee wala kuendesha gari kupitia maji ya mafuriko. "
                "Ikiwa kuhama si salama, baki katika sehemu ya juu "
                "na salama zaidi inayopatikana na uombe msaada."
            ),
            "fr": (
                "Ne marchez pas et ne conduisez pas dans les eaux de crue. "
                "Si vous ne pouvez pas vous déplacer sans danger, restez "
                "dans l'endroit en hauteur le plus sûr disponible et "
                "demandez de l'aide."
            ),
        },


        # ====================================================
        # FLOOD — HIGH CURRENT ACTION
        # ====================================================

        (
            "Stay away from low-lying areas and floodwater, "
            "and prepare to move to a safer elevated location "
            "before conditions become more dangerous."
        ): {
            "ar": (
                "ابتعد عن المناطق المنخفضة ومياه الفيضانات، "
                "واستعد للانتقال إلى مكان مرتفع وأكثر أمانًا "
                "قبل أن تصبح الظروف أكثر خطورة."
            ),
            "sw": (
                "Kaa mbali na maeneo ya chini na maji ya mafuriko, "
                "na jiandae kuhamia sehemu ya juu na salama zaidi "
                "kabla hali haijawa hatari zaidi."
            ),
            "fr": (
                "Restez à l'écart des zones basses et des eaux de crue, "
                "et préparez-vous à rejoindre un endroit plus sûr et "
                "en hauteur avant que la situation ne devienne plus dangereuse."
            ),
        },


        # ====================================================
        # FLOOD — HIGH BACKUP ACTION
        # ====================================================

        (
            "Do not enter flooded roads or moving water. If "
            "water begins rising around you, move to higher "
            "ground if it is safe to do so."
        ): {
            "ar": (
                "لا تدخل الطرق المغمورة بالمياه ولا تعبر المياه الجارية. "
                "إذا بدأت المياه ترتفع حولك، فانتقل إلى مكان مرتفع "
                "إذا كان ذلك آمنًا."
            ),
            "sw": (
                "Usiingie kwenye barabara zilizofurika wala kuvuka maji "
                "yanayotiririka. Maji yakianza kupanda karibu nawe, "
                "hamia sehemu ya juu ikiwa ni salama kufanya hivyo."
            ),
            "fr": (
                "N'empruntez pas les routes inondées et ne traversez pas "
                "les eaux en mouvement. Si l'eau commence à monter autour "
                "de vous, rejoignez un terrain plus élevé si vous pouvez "
                "le faire sans danger."
            ),
        },


        # ====================================================
        # FLOOD — MODERATE CURRENT ACTION
        # ====================================================

        (
            "Avoid low-lying and flood-prone areas and keep "
            "a safe route to higher ground available."
        ): {
            "ar": (
                "تجنب المناطق المنخفضة والمعرضة للفيضانات، "
                "واحرص على وجود طريق آمن يمكنك استخدامه للوصول "
                "إلى مكان مرتفع."
            ),
            "sw": (
                "Epuka maeneo ya chini na yanayokabiliwa na mafuriko, "
                "na hakikisha una njia salama ya kufikia sehemu ya juu."
            ),
            "fr": (
                "Évitez les zones basses et exposées aux inondations, "
                "et gardez un itinéraire sûr disponible pour rejoindre "
                "un endroit plus élevé."
            ),
        },


        # ====================================================
        # FLOOD — MODERATE BACKUP ACTION
        # ====================================================

        (
            "Stay away from floodwater. If water levels begin "
            "to rise or nearby routes become unsafe, move to "
            "a safer elevated location."
        ): {
            "ar": (
                "ابتعد عن مياه الفيضانات. إذا بدأت مستويات المياه "
                "في الارتفاع أو أصبحت الطرق القريبة غير آمنة، "
                "فانتقل إلى مكان مرتفع وأكثر أمانًا."
            ),
            "sw": (
                "Kaa mbali na maji ya mafuriko. Ikiwa kiwango cha maji "
                "kinaanza kupanda au njia za karibu zinakuwa si salama, "
                "hamia sehemu ya juu na salama zaidi."
            ),
            "fr": (
                "Restez à l'écart des eaux de crue. Si le niveau de l'eau "
                "commence à monter ou si les routes proches deviennent "
                "dangereuses, rejoignez un endroit plus sûr et en hauteur."
            ),
        },


        # ====================================================
        # FLOOD — LOW CURRENT ACTION
        # ====================================================

        (
            "Stay away from floodwater and avoid low-lying areas "
            "where water may collect."
        ): {
            "ar": (
                "ابتعد عن مياه الفيضانات وتجنب المناطق المنخفضة "
                "التي قد تتجمع فيها المياه."
            ),
            "sw": (
                "Kaa mbali na maji ya mafuriko na epuka maeneo ya chini "
                "ambako maji yanaweza kujikusanya."
            ),
            "fr": (
                "Restez à l'écart des eaux de crue et évitez les zones "
                "basses où l'eau peut s'accumuler."
            ),
        },


        # ====================================================
        # FLOOD — LOW BACKUP ACTION
        # ====================================================

        (
            "If local water levels begin rising, move away from "
            "the affected area and use a safe route toward higher ground."
        ): {
            "ar": (
                "إذا بدأت مستويات المياه المحلية في الارتفاع، "
                "فابتعد عن المنطقة المتأثرة واستخدم طريقًا آمنًا "
                "نحو مكان مرتفع."
            ),
            "sw": (
                "Ikiwa kiwango cha maji katika eneo lako kinaanza kupanda, "
                "ondoka kwenye eneo lililoathiriwa na tumia njia salama "
                "kuelekea sehemu ya juu."
            ),
            "fr": (
                "Si le niveau de l'eau commence à monter dans votre zone, "
                "éloignez-vous de la zone touchée et empruntez un itinéraire "
                "sûr vers un terrain plus élevé."
            ),
        },


        # ====================================================
        # FLOOD — BLOCKED ROUTE CURRENT ACTION
        # ====================================================

        (
            "Do not use routes reported as blocked or "
            "flooded. Turn back and use another route only "
            "if it is confirmed safe."
        ): {
            "ar": (
                "لا تستخدم الطرق المُبلغ عن انسدادها أو غمرها بالمياه. "
                "ارجع ولا تستخدم طريقًا بديلًا إلا إذا تم تأكيد أمانه."
            ),
            "sw": (
                "Usitumie njia zilizoripotiwa kuwa zimefungwa au zimefurika. "
                "Geuka na urudi, na tumia njia nyingine tu ikiwa imethibitishwa "
                "kuwa salama."
            ),
            "fr": (
                "N'empruntez pas les routes signalées comme bloquées ou inondées. "
                "Faites demi-tour et n'utilisez un autre itinéraire que si sa "
                "sécurité est confirmée."
            ),
        },


        # ====================================================
        # FLOOD — BLOCKED ROUTE BACKUP ACTION
        # ====================================================

        (
            "If no safe route is confirmed, remain in the "
            "safest available location away from floodwater "
            "and request assistance."
        ): {
            "ar": (
                "إذا لم يتم تأكيد طريق آمن، فابقَ في أكثر مكان آمن "
                "متاح بعيدًا عن مياه الفيضانات واطلب المساعدة."
            ),
            "sw": (
                "Ikiwa hakuna njia salama iliyothibitishwa, baki katika sehemu "
                "salama zaidi inayopatikana, mbali na maji ya mafuriko, "
                "na uombe msaada."
            ),
            "fr": (
                "Si aucun itinéraire sûr n'est confirmé, restez dans l'endroit "
                "le plus sûr disponible, loin des eaux de crue, et demandez "
                "de l'aide."
            ),
        },
    }
)

# ============================================================
# HELPERS
# ============================================================


def _normalize_text(
    value,
) -> str:
    """
    Normalize whitespace without changing message meaning.
    """

    if value is None:
        return ""

    return " ".join(
        str(value).split()
    ).strip()


def _normalize_language(
    language,
) -> str:
    """
    Normalize a requested communication language.

    Supported base languages:
    - en
    - ar
    - sw
    - fr

    Regional variants are reduced to their base language:
    - ar-EG -> ar
    - fr-FR -> fr
    - sw-KE -> sw
    - en_US -> en

    Unsupported or invalid values safely fall back to English.
    """

    if not isinstance(
        language,
        str,
    ):
        return "en"

    normalized = (
        language
        .strip()
        .lower()
        .replace(
            "_",
            "-",
        )
    )

    if not normalized:
        return "en"

    base_language = normalized.split(
        "-",
        1,
    )[0]

    if base_language not in SUPPORTED_LANGUAGES:
        return "en"

    return base_language
# ============================================================
# LOCALIZE APPROVED ACTION
# ============================================================


def localize_action(
    text,
    language,
) -> str:
    """
    Return an approved deterministic translation.

    Safety behavior:
    - English returns the original approved action.
    - Known action + supported language returns approved text.
    - Unknown action returns the original English action.
    - Missing translation returns the original English action.
    - Never generates or invents an emergency instruction.
    """

    source_text = _normalize_text(
        text
    )

    if not source_text:
        return ""

    normalized_language = _normalize_language(
        language
    )

    if normalized_language == "en":
        return source_text

    translations = ACTION_TRANSLATIONS.get(
        source_text
    )

    if not translations:
        return source_text

    translated = translations.get(
        normalized_language
    )

    if not translated:
        return source_text

    return _normalize_text(
        translated
    )


# ============================================================
# CATALOG VALIDATION
# ============================================================


def validate_translation_catalog() -> list[str]:
    """
    Validate the deterministic translation catalog.

    Returns a list of validation errors.
    An empty list means the catalog is structurally valid.
    """

    errors: list[str] = []

    for source_text, translations in ACTION_TRANSLATIONS.items():

        normalized_source = _normalize_text(
            source_text
        )

        if not normalized_source:
            errors.append(
                "Translation catalog contains an empty source action."
            )
            continue

        if not isinstance(
            translations,
            dict,
        ):
            errors.append(
                f"Translations for action {normalized_source!r} "
                "must be a dictionary."
            )
            continue

        for language in REQUIRED_TRANSLATION_LANGUAGES:

            translated = _normalize_text(
                translations.get(
                    language
                )
            )

            if not translated:
                errors.append(
                    f"Missing {language!r} translation for action "
                    f"{normalized_source!r}."
                )

    return errors