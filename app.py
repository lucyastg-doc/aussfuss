import streamlit as st
from scoring import (
    compute_fuss, compute_auss,
    severity_from_score, recommend_treatment,
    format_report_docx_web
)

st.set_page_config(page_title="AUSS/FUSS", layout="centered")

st.markdown("""<style>
/* Brand palette */
:root{
  --aussfuss-purple:#7A4BAE;
  --aussfuss-green:#4BAF8B;
  --aussfuss-green-bg:#E9F7EF;
  --aussfuss-text:#0F172A;
}

/* App background */
div[data-testid="stAppViewContainer"]{
  background: var(--aussfuss-green-bg) !important;
}
header[data-testid="stHeader"]{
  background: rgba(233,247,239,0.85) !important;
}

/* Layout */
.block-container{
  padding-top: 1.2rem !important;
  padding-bottom: 2rem !important;
  max-width: 980px !important;
}

/* Criteria labels (bigger than options) */
div[data-testid="stWidgetLabel"] > label p,
div[data-testid="stWidgetLabel"] p{
  font-size: 20px !important;
  font-weight: 800 !important;
  color: var(--aussfuss-text) !important;
  margin-bottom: 0.15rem !important;
}

/* Options text */
div[role="radiogroup"] label p,
div[role="listbox"] li,
div[data-baseweb="select"] span,
div[data-testid="stSelectbox"] p,
div[data-testid="stMultiSelect"] p{
  font-size: 16px !important;
  font-weight: 400 !important;
  color: var(--aussfuss-text) !important;
}

/* Checkbox label (breakdown) — smaller and not bold */
div[data-testid="stCheckbox"] label p{
  font-size: 14px !important;
  font-weight: 400 !important;
}

/* Buttons */
div.stButton > button{
  background: var(--aussfuss-purple) !important;
  color: white !important;
  border-radius: 12px !important;
  border: 0 !important;
  padding: 0.65rem 1.1rem !important;
}
div.stButton > button:hover{ filter: brightness(0.95); }

/* Result box */
.result-box{
  border-left: 6px solid var(--aussfuss-purple) !important;
  background: #f5f3ff !important;
  padding: 14px 14px !important;
  border-radius: 14px !important;
}

/* Tabs */
button[data-baseweb="tab"] p{
  font-size: 16px !important;
  font-weight: 700 !important;
  color: var(--aussfuss-text) !important;
}
button[data-baseweb="tab"][aria-selected="true"] p{ color: var(--aussfuss-purple) !important; }
div[data-baseweb="tab-highlight"]{ background-color: var(--aussfuss-purple) !important; }
div[data-baseweb="tab-list"]{ border-bottom: 1px solid rgba(15,23,42,0.12) !important; }

/* Remove red error accents if any */
.stAlert, .stException{
  border-left-color: var(--aussfuss-purple) !important;
}

/* Title branding */
.aussfuss-title{font-size:54px;font-weight:900;letter-spacing:0.4px;line-height:1;margin:0 0 6px 0;}
.aussfuss-title .purple{color:var(--aussfuss-purple);}
.aussfuss-title .green{color:var(--aussfuss-green);}
.aussfuss-title .divider{color:rgba(15,23,42,0.55);font-weight:800;padding:0 10px;}
.aussfuss-subtitle{font-size:20px;font-weight:700;opacity:0.9;margin:0 0 16px 0;}
/* Breakdown title (smaller, not bold) */
.breakdown-title{font-size:14px;font-weight:500;opacity:0.85;margin:6px 0 6px 0;}

</style>""",
    unsafe_allow_html=True
)

col_logo, col_title = st.columns([1, 4], vertical_alignment="center")
with col_logo:
    st.image("assets/aussfuss_logo.png", width=220)
with col_title:
    st.markdown("<div class='aussfuss-title'><span class='purple'>AUSS</span> <span class='divider'>/</span> <span class='green'>FUSS</span></div>", unsafe_allow_html=True)
    st.markdown('<div class="aussfuss-subtitle">Оценка степени тяжести поражения роговицы и выбор тактики лечения</div>', unsafe_allow_html=True)

st.markdown("")
left, right = st.columns([3,1], vertical_alignment="center")
with left:
    st.markdown('<span class="pill">Веб-версия (без персональных данных)</span>', unsafe_allow_html=True)
with right:
    show_breakdown = st.checkbox("Разложение по баллам", value=False)

st.markdown('<div class="hint">Заполните анкету согласно клиническим данным пациента и нажмите кнопку <b>«Рассчитать»</b>. После расчёта сохраните протокол в формате DOCX.</div>', unsafe_allow_html=True)



st.divider()
tabs = st.tabs(["0) Выбор шкалы", "1) Клиника", "2) ОКТ", "3) Конфокальная микроскопия"])

with tabs[0]:
    st.markdown("### Калькулятор AUSS/FUSS")
    etiology = st.selectbox(
        "Шкала",
        ["AUSS (акантамебная этиология)", "FUSS (грибковая этиология)", "Неизвестно (посчитать обе шкалы)"],
        index=0
    )

def crit(txt: str):
    st.markdown(f'<div class="crit">{txt}</div>', unsafe_allow_html=True)

with tabs[1]:
    st.markdown("### Клиника")

    crit("Болевой синдром")
    pain = st.radio("", options=[0,2,4], key="pain",
                    format_func=lambda x: {0:"нет/умеренный",2:"умеренный",4:"выраженный"}[x],
                    label_visibility="collapsed")

    crit("Перикорнеальная инъекция")
    injection = st.radio("", options=[0,1,2,3], key="inj",
                         format_func=lambda x: ["нет","лёгкая","средняя","выраженная"][x],
                         label_visibility="collapsed")

    crit("Отделяемое")
    discharge = st.radio("", options=[0,1], key="disch",
                         format_func=lambda x: "нет" if x==0 else "есть",
                         label_visibility="collapsed")

    crit("Сателлитные инфильтраты или «перистые» края")
    satellites = st.radio("", options=[0,1], key="sat",
                          format_func=lambda x: "нет" if x==0 else "есть",
                          label_visibility="collapsed")

    crit("Размер инфильтрата/язвенного дефекта (мм) — вводится вручную")
    size_mm = st.number_input("", min_value=0.0, max_value=20.0, value=2.0, step=0.1, key="size_mm", label_visibility="collapsed")

    crit("Локализация")
    localization = st.radio("", options=["peripheral","paracentral","central"], key="loc",
                            format_func=lambda x: { "peripheral":"периферия","paracentral":"парацентрально","central":"центральная зона" }[x],
                            label_visibility="collapsed")

    crit("Глубина язвенного дефекта")
    depth_cat = st.radio("", options=["superficial","mid","deep","descemetocele"], key="depth",
                         format_func=lambda x: {
                             "superficial":"до поверхностных слоёв стромы",
                             "mid":"до средних слоёв стромы",
                             "deep":"до глубоких слоёв стромы",
                             "descemetocele":"десцеметоцеле / перфорация"
                         }[x],
                         label_visibility="collapsed")

    crit("Признаки десцеметита")
    descemetitis = st.radio("", options=[0,1], key="desc",
                            format_func=lambda x: "нет" if x==0 else "есть",
                            label_visibility="collapsed")

    crit("Гипопион (уровень)")
    hypopyon = st.radio("", options=["none","lt1","1to2","gt2"], key="hyp",
                        format_func=lambda x: {"none":"нет","lt1":"<1 мм","1to2":"1–2 мм","gt2":">2 мм"}[x],
                        label_visibility="collapsed")

    crit("Тотальное бельмо (плотное диффузное помутнение)")
    total_leucoma = st.radio("", options=[0,1], key="leu",
                             format_func=lambda x: "нет" if x==0 else "есть",
                             label_visibility="collapsed")

    crit("Состояние передней камеры ")
    ac = st.radio("", options=["0","1-20",">20","not_visible"], key="ac",
                  format_func=lambda x: {
                      "0":"нет клеток",
                      "1-20":"1–20 клеток",
                      ">20":">20 клеток",
                      "not_visible":"передняя камера не просматривается"
                  }[x],
                  label_visibility="collapsed")

    crit("Отёк роговицы (по клинике/ОКТ)")
    edema = st.radio("", options=[0,1,2], key="edema",
                     format_func=lambda x: ["нет","умеренный","выраженный"][x],
                     label_visibility="collapsed")

    crit("Внутриглазное давление")
    iog = st.radio("", options=["normal","high","low"], key="iog",
                   format_func=lambda x: {"normal":"норма","high":"повышено","low":"понижено"}[x],
                   label_visibility="collapsed")

    crit("Вовлечение лимба")
    limbal = st.radio("", options=[0,1], key="limb",
                      format_func=lambda x: "нет" if x==0 else "есть",
                      label_visibility="collapsed")

    crit("Прогнозируемая интенсивность помутнения (по клинике)")
    opacity = st.radio("", options=[0,1,2], key="opac",
                       format_func=lambda x: ["незначительное","умеренное","грубое со снижением остроты зрения"][x],
                       label_visibility="collapsed")

    st.divider()
    st.markdown("### Специфические клинические признаки")

    fungal_form = 0
    progress_speed_f = 0
    amoeba_form = 0
    pseudo_dendrite = 0
    ring = 0
    rk_clin = 0
    delay_therapy = 0
    progress_speed_a = 0

    if etiology in ["FUSS (грибковая этиология)", "Неизвестно (посчитать обе шкалы)"]:
        st.markdown("#### FUSS (грибковая этиология)")
        crit("Клиническая форма")
        fungal_form = st.radio("", options=[0,1,2], key="f_form",
                               format_func=lambda x: {0:"нет специфических признаков",1:"творожистый инфильтрат",2:"мицелий-подобное помутнение"}[x],
                               label_visibility="collapsed")
        crit("Скорость клинического прогрессирования")
        progress_speed_f = st.radio("", options=[0,1,2], key="f_speed",
                                    format_func=lambda x: {0:"медленная",1:"быстрая",2:"молниеносная"}[x],
                                    label_visibility="collapsed")

    if etiology in ["AUSS (акантамебная этиология)", "Неизвестно (посчитать обе шкалы)"]:
        st.markdown("#### AUSS (акантамебная этиология)")
        crit("Клиническая форма")
        amoeba_form = st.radio("", options=[0,1,2,3,4], key="a_form",
                               format_func=lambda x: {
                                   0:"поверхностный эпителиальный кератит",
                                   1:"поверхностный точечный кератит",
                                   2:"стромальный кольцевидный кератит",
                                   3:"язва роговицы",
                                   4:"кератит и склерит"
                               }[x],
                               label_visibility="collapsed")
        crit("Эпителиальный дефект / псевдодендрит")
        pseudo_dendrite = st.radio("", options=[0,1], key="a_pseudo",
                                   format_func=lambda x: "нет" if x==0 else "есть",
                                   label_visibility="collapsed")
        crit("Кольцевидный инфильтрат")
        ring = st.radio("", options=[0,1,2], key="a_ring",
                        format_func=lambda x: {0:"нет",1:"формируется",2:"сформирован"}[x],
                        label_visibility="collapsed")
        crit("Радиальный кератоневрит (клиника)")
        rk_clin = st.radio("", options=[0,1], key="a_rk",
                           format_func=lambda x: "нет" if x==0 else "есть",
                           label_visibility="collapsed")
        crit("Длительность до специфической терапии")
        delay_therapy = st.radio("", options=[0,1,2], key="a_delay",
                                 format_func=lambda x: {0:"≤7 дней",1:"8–21 день",2:">21 дня"}[x],
                                 label_visibility="collapsed")
        crit("Скорость клинического прогрессирования")
        progress_speed_a = st.radio("", options=[0,1,2], key="a_speed",
                                    format_func=lambda x: {0:"медленная",1:"быстрая",2:"молниеносная"}[x],
                                    label_visibility="collapsed")

with tabs[2]:
    st.markdown("### ОКТ (пахиметрия)")

    crit("Минимальная толщина в зоне дефекта (мкм)")
    min_thickness_um = st.number_input("", min_value=0, max_value=1200, value=400, step=1, key="min_th", label_visibility="collapsed")

    crit("Средняя толщина роговицы (пахиметрия, мкм)")
    mean_thickness_um = st.number_input("", min_value=0, max_value=1200, value=600, step=1, key="mean_th", label_visibility="collapsed")

    crit("Локальные зоны истончения / неравномерность пахиметрии")
    pachy_uneven = st.radio("", options=[0,1], key="pachy",
                            format_func=lambda x: "нет" if x==0 else "есть",
                            label_visibility="collapsed")

    thinning_progress_72h = 0
    if etiology in ["FUSS (грибковая этиология)", "Неизвестно (посчитать обе шкалы)"]:
        crit("Прогрессирование истончения за 48–72 ч (FUSS)")
        thinning_progress_72h = st.radio("", options=[0,1], key="thin72",
                                         format_func=lambda x: "нет" if x==0 else "есть",
                                         label_visibility="collapsed")

with tabs[3]:
    st.markdown("### Конфокальная микроскопия")
    hyphae = hyphae_depth = 0
    cysts = troph = rk_conf = 0

    if etiology in ["FUSS (грибковая этиология)", "Неизвестно (посчитать обе шкалы)"]:
        st.markdown("#### FUSS")
        crit("Грибковые гифы и/или споры")
        hyphae = st.radio("", options=[0,1,2,3], key="hyphae",
                          format_func=lambda x: {0:"не выявлены",1:"единичные",2:"множественные",3:"массивные"}[x],
                          label_visibility="collapsed")
        crit("Глубина залегания гифов и/или спор")
        hyphae_depth = st.radio("", options=[0,1,2,3], key="hy_depth",
                        format_func=lambda x: {0:"нет",1:"эпителий/поверхностная строма",2:"средняя строма",3:"глубокая строма"}[x],
                        label_visibility="collapsed")

    if etiology in ["AUSS (акантамебная этиология)", "Неизвестно (посчитать обе шкалы)"]:
        st.markdown("#### AUSS")
        crit("Акантамебные цисты")
        cysts = st.radio("", options=[0,1,2,3], key="cysts",
                         format_func=lambda x: {0:"не выявлены",1:"единичные",2:"множественные",3:"массивные"}[x],
                         label_visibility="collapsed")
        crit("Трофозоиты")
        troph = st.radio("", options=[0,1], key="troph",
                         format_func=lambda x: "нет" if x==0 else "есть",
                         label_visibility="collapsed")
        crit("Глубина залегания цист/трофозоитов")
        amoeba_depth = st.radio("", options=[0,1,2,3], key="amoeba_depth",
                                format_func=lambda x: {0:"нет",1:"эпителий/поверхностная строма",2:"средняя строма",3:"глубокая строма"}[x],
                                label_visibility="collapsed")

        crit("Признаки кератоневрита (конфокальная микроскопия)")
        rk_conf = st.radio("", options=[0,1], key="rk_conf",
                           format_func=lambda x: "нет" if x==0 else "есть",
                           label_visibility="collapsed")

st.divider()
calc = st.button("Рассчитать")

# автоматическая категоризация размера по введённому значению
mm = float(st.session_state.get("size_mm", 2.0))
if mm <= 2: size_cat = "<=2"
elif mm <= 4: size_cat = "2-4"
elif mm <= 6: size_cat = "4-6"
else: size_cat = ">6"

base = dict(
    pain=pain, injection=injection, discharge=discharge, satellites=satellites,
    size_cat=size_cat, localization=localization, depth_cat=depth_cat,
    descemetitis=descemetitis, hypopyon=hypopyon, total_leucoma=total_leucoma,
    ac=ac, edema=edema, iog=iog, limbal=limbal, opacity=opacity,
    min_thickness_um=min_thickness_um, mean_thickness_um=mean_thickness_um,
    pachy_uneven=pachy_uneven, thinning_progress_72h=thinning_progress_72h
)

if calc:
    results = []

    if etiology in ["FUSS (грибковая этиология)", "Неизвестно (посчитать обе шкалы)"]:
        ctx_f = dict(base)
        ctx_f.update(dict(
            fungal_form=fungal_form,
            progress_speed=progress_speed_f,
            hyphae=hyphae,
            hyphae_depth=hyphae_depth,
        ))
        res = compute_fuss(ctx_f)
        sev = severity_from_score(res.score, "FUSS", critical=res.critical)
        rec = recommend_treatment("FUSS", sev, res.score, ctx_f, critical=res.critical)
        results.append(("FUSS", res, sev, rec))

    if etiology in ["AUSS (акантамебная этиология)", "Неизвестно (посчитать обе шкалы)"]:
        ctx_a = dict(base)
        ctx_a.update(dict(
            amoeba_form=amoeba_form,
            pseudo_dendrite=pseudo_dendrite,
            ring=ring,
            rk_clin=rk_clin,
            delay_therapy=delay_therapy,
            progress_speed=progress_speed_a,
            cysts=cysts, troph=troph, rk_conf=rk_conf
        ))
        res = compute_auss(ctx_a)
        sev = severity_from_score(res.score, "AUSS", critical=res.critical)
        rec = recommend_treatment("AUSS", sev, res.score, ctx_a, critical=res.critical)
        results.append(("AUSS", res, sev, rec))

    for scale, res, sev, rec in results:
        st.markdown(f"## Результат — {scale}")
        c1, c2 = st.columns(2)
        c1.metric("Сумма баллов", res.score)
        c2.metric("Степень тяжести", sev)

        st.markdown("## Рекомендации")
        st.markdown('<div class="result-box">', unsafe_allow_html=True)
        st.write(rec)
        st.markdown('</div>', unsafe_allow_html=True)

        if show_breakdown:
            st.markdown("<div class='breakdown-title'>Разложение баллов</div>", unsafe_allow_html=True)
            st.json(res.breakdown, expanded=False)

        docx_bytes, filename = format_report_docx_web(
    scale=scale,
    score=res.score,
    severity=sev,
    recommendation=rec,
    breakdown=res.breakdown if show_breakdown else None
)

        st.download_button("Скачать протокол (DOCX)", data=docx_bytes, file_name=filename,
                           mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        st.divider()
