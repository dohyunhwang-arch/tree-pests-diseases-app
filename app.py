# -*- coding: utf-8 -*-
import streamlit as st
import json
import random
import os
import time

# 페이지 기본 설정
st.set_page_config(
    page_title="나무의사 2차 실기 & 필기 완벽 대비 학습 도우미",
    page_icon="🌲",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========================================================
# 🔒 스터디원 전용 비밀번호 인증 시스템
# ========================================================
# 기본 비밀번호 (원하시는 비밀번호로 자유롭게 변경 가능합니다)
DEFAULT_STUDY_PASSWORD = "td2026"

def check_study_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        # 로그인 화면 UI
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown("### 🔒 나무의사 스터디 전용 학습 도우미")
                st.caption("AI응용 데이터분석 스터디원만 이용 가능한 비공개 학습 공간입니다.")
                st.markdown("---")
                
                input_pwd = st.text_input(
                    "스터디 비밀번호를 입력하세요:",
                    type="password",
                    placeholder="비밀번호 입력 후 Enter 또는 접속 버튼 클릭",
                    key="login_pwd_input"
                )
                
                # Streamlit Secrets에 설정된 비밀번호가 있다면 우선 사용, 없으면 기본값 사용
                correct_pwd = st.secrets.get("STUDY_PASSWORD", DEFAULT_STUDY_PASSWORD)
                
                if st.button("🚀 스터디 룸 입장하기", type="primary", use_container_width=True):
                    if input_pwd == correct_pwd:
                        st.session_state.authenticated = True
                        st.success("인증되었습니다! 학습 화면으로 이동합니다.")
                        st.rerun()
                    else:
                        st.error("비밀번호가 올바르지 않습니다. 스터디 리더에게 문의하세요.")
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.info("💡 **초기 비밀번호:** `td2026`\n\n(비밀번호 변경은 app.py 상단의 DEFAULT_STUDY_PASSWORD에서 수정하실 수 있습니다.)")
        
        # 비밀번호를 맞히기 전까지는 하단 도감 데이터 및 퀴즈 구동을 완전히 중단
        st.stop()

check_study_password()


# 데이터 로딩 함수 (캐싱 적용)
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, "data", "tree_pests_diseases.json")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

ALL_ITEMS = load_data()

# 에빙하우스 복습 주기 (일수)
# Box 1: 오늘(0일), Box 2: 1일 뒤, Box 3: 3일 뒤, Box 4: 7일 뒤, Box 5: 15일 뒤(마스터)
EB_INTERVALS = [0, 1, 3, 7, 15]

# 세션 상태 초기화 (에빙하우스 학습 데이터 & 퀴즈 상태)
if "eb_state" not in st.session_state:
    st.session_state.eb_state = {}
    for item in ALL_ITEMS:
        st.session_state.eb_state[item["id"]] = {
            "box": 1,
            "next_review": time.time(),
            "correct_count": 0,
            "wrong_count": 0
        }

if "current_quiz" not in st.session_state:
    st.session_state.current_quiz = None

if "quiz_img_idx" not in st.session_state:
    st.session_state.quiz_img_idx = 0

if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

if "selected_choice" not in st.session_state:
    st.session_state.selected_choice = None

# AI 맞춤형 암기 팁 생성 함수
def get_mnemonic_tip(item):
    name = item.get("name", "")
    tree = item.get("tree_name", "")
    ptype = item.get("type", "")
    pathogen = item.get("scientific_or_en_name") or item.get("pathogen", "")
    control = item.get("control_method", "")

    if "재선충병" in name:
        if "소나무" in tree:
            return {
                "tag": "⭐️ 2차 실기 1순위 초특급 빈출",
                "tip": "【소·솔 / 잣·북】 공식 암기! 소나무는 솔수염하늘소, 잣나무는 북방수염하늘소가 매개충입니다. 증상은 '우산살 모양'으로 아래로 처지며 적갈색 고사. 병원체는 선충(Bursaphelenchus xylophilus). 예방 나무주사는 12~2월 아바멕틴·에마멕틴벤조에이트 유제!"
            }
        else:
            return {
                "tag": "⭐️ 2차 실기 1순위 초특급 빈출",
                "tip": "잣나무 재선충병 매개충은 '북방수염하늘소'! 유충은 윗입술 등면에 강모가 있어 솔수염하늘소 유충과 구분됩니다. 방제는 고사목 훈증/파쇄 및 나무주사(아바멕틴)."
            }
    if "빗자루병" in name:
        return {
            "tag": "⭐️ 병원체 식별 핵심",
            "tip": "빗자루병은 곰팡이가 아니라 【파이토플라스마(Phytoplasma)】! 세포벽이 없는 세균 유사 미생물입니다. 대추나무 빗자루병 매개충은 '모무늬매미충', 방제 약제는 옥시테트라사이클린(테트라사이클린계 수간주사) 필수 암기!"
        }
    if "흰가루병" in name:
        return {
            "tag": "⭐️ 병원체 자낭구 부속사 식별",
            "tip": "흰가루병은 늦여름~가을 밀식/통풍 불량지 다발. 2차 실기 현미경 문제 단골! 자낭구(폐낭각)의 부속사 형태(균사상, 갈고리형, 분지형, 침형)와 자낭 수(1개 vs 여러 개)를 묻는 문제가 자주 출제됩니다."
        }
    if "녹병" in name:
        return {
            "tag": "⭐️ 중간기주(기주교대) 필수 암기",
            "tip": "녹병은 대표적인 담자균문(Rusts) 이종기생균! 【기주교대(중간기주)】가 핵심입니다. 소나무 잎녹병(황벽나무/참취), 배나무 붉은별무늬병(향나무), 잣나무 털녹병(송이풀/까치밥나무) 교대기주를 서로 1~2km 격리하는 것이 생태적 방제의 핵심!"
        }
    if "그을음병" in name:
        return {
            "tag": "⭐️ 복합 원인 연계 암기",
            "tip": "그을음병은 병원균 단독 감염이 아니라, 【진딧물·깍지벌레·가루이】의 감로(배설물)를 영양분 삼아 2차적으로 번식하는 부생균입니다. 살균제보다 흡즙 해충 구제가 근본 방제법!"
        }
    if "피목가지마름병" in name:
        return {
            "tag": "⭐️ 수세 쇠약목 판정",
            "tip": "Cenangium 가지마름병은 가뭄, 이식 충격, 이상기온 등으로 수세가 급격히 약해진 소나무림에 대발생합니다. 병환부에 흑갈색 접시 모양 자실체(반자낭반) 형성!"
        }
    if "아밀라리아" in name or "뿌리썩음병" in name:
        return {
            "tag": "⭐️ 뿌리 병해 감별 팁",
            "tip": "아밀라리아는 수피 아래 '흰색 균사판'과 땅속 '근상균사다발(철사 모양 균사박)'이 결정적 동정 키! 가을철 뽕나무버섯 자실체 발생. 리지나뿌리썩음병은 산불/모닥불 터 고온 자극 후 발아하는 특징과 비교!"
        }
    if "하늘소" in name or "좀" in name:
        return {
            "tag": "⭐️ 천공성 해충 방제 공식",
            "tip": "줄기·수피 속에 숨어 가해하므로 접촉성 살충제로는 방제가 어렵습니다. '목질부 톱밥 배출' 흔적으로 조기 발견, 침투이행성 약제 주입 또는 우화기 살포 및 고사목 벌채 훈증이 핵심!"
        }
    if "깍지벌레" in name or "진딧물" in name:
        return {
            "tag": "⭐️ 흡즙성 해충 방제 적기",
            "tip": "깍지벌레는 밀랍 왁스층이 생기기 전인 【1령 약충 부화 이동기(5~6월)】가 방제 골든타임! 성충은 껍질 때문에 약제 침투가 어려우므로 기계유유제(월동기)나 침투이행성 네오니코티노이드계를 사용합니다."
        }
    if "나방" in name or "잎벌" in name:
        return {
            "tag": "⭐️ 식엽성 해충 생활사 팁",
            "tip": "유충 어릴 때는 거미줄(실)을 토해 집단으로 모여 잎을 가해하다가, 종령 유충이 되면 흩어져 폭식합니다. 집단 서식기(1~3령)에 가지째 잘라 소각하거나 유기인계/비티(Bt)균제 살포!"
        }
    if "응애" in name:
        return {
            "tag": "⭐️ 미소 해충 연상 공식",
            "tip": "고온 건조기(7~8월)에 엽록소를 빨아먹어 잎이 탈색(회백색 반점)됩니다. 곤충이 아닌 거미강이므로 일반 살충제가 아닌 【살비제(Acaricide)】를 사용해야 하며, 약제 저항성이 매우 강해 교차 살포 필수!"
        }

    keyword = f"병원체/학명: '{pathogen}'" if pathogen else ""
    action = f"{control[:60]}..." if control else "적기 약제 방제와 위생 간벌 병행"
    return {
        "tag": f"💡 [{tree} {name}] 합격 핵심 키워드",
        "tip": f"【기주-증상 연계】 {tree}에서 주로 발생하는 {ptype}입니다. {keyword} 2차 서술 시 방제 요령: {action}"
    }

# 퀴즈 문제 생성 함수
def generate_new_quiz():
    now = time.time()
    # 사진이 있는 항목 대상
    photo_items = [it for it in ALL_ITEMS if it.get("images") and len(it.get("images")) > 0]
    
    # 에빙하우스 복습 대상자 우선 추출
    due_items = [it for it in photo_items if st.session_state.eb_state[it["id"]]["next_review"] <= now]
    target_pool = due_items if due_items else photo_items
    
    target = random.choice(target_pool)
    
    # 오답 보기 3개 추출 (동일 구분의 다른 병해충)
    same_type_items = [it for it in ALL_ITEMS if it["type"] == target["type"] and it["id"] != target["id"]]
    distractors = random.sample(same_type_items, min(3, len(same_type_items)))
    
    choices = [target] + distractors
    random.shuffle(choices)
    
    st.session_state.current_quiz = target
    st.session_state.quiz_choices = choices
    st.session_state.quiz_img_idx = 0
    st.session_state.quiz_submitted = False
    st.session_state.selected_choice = None

# 첫 퀴즈 초기화
if st.session_state.current_quiz is None:
    generate_new_quiz()

# 사이드바 구성
with st.sidebar:
    st.title("🌲 나무의사 합격 도우미")
    st.markdown("---")
    
    # 모드 선택
    mode = st.radio(
        "메뉴 선택",
        ["🎯 2차 실기 식별 퀴즈 (에빙하우스)", "📖 병해충 도감 검색 (전수 539종)"],
        index=0
    )
    
    st.markdown("---")
    st.subheader("🧠 에빙하우스 망각곡선 현황")
    
    # 박스별 개수 집계
    box_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for s in st.session_state.eb_state.values():
        b = max(1, min(s["box"], 5))
        box_counts[b] += 1
        
    st.write(f"• **Box 1 (오늘 복습)**: {box_counts[1]}개")
    st.write(f"• **Box 2 (1일 후)**: {box_counts[2]}개")
    st.write(f"• **Box 3 (3일 후)**: {box_counts[3]}개")
    st.write(f"• **Box 4 (7일 후)**: {box_counts[4]}개")
    st.write(f"• **Box 5 (완전 마스터)**: {box_counts[5]}개")
    
    st.caption("※ 오답 시 즉시 Box 1로 강등되어 오늘 반복 출제됩니다.")

# ========================================================
# 화면 1: 에빙하우스 2차 실기 식별 퀴즈
# ========================================================
if mode == "🎯 2차 실기 식별 퀴즈 (에빙하우스)":
    st.subheader("🎯 나무의사 2차 실기 수목 병해충 사진 식별 퀴즈")
    st.caption("나무의사 2차 실기시험에 출제되는 사진 식별 훈련입니다. 사진과 증상을 관찰하고 올바른 병해충명을 맞혀보세요.")

    quiz = st.session_state.current_quiz

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown(f"### 🌿 기주 수목: **{quiz['tree_name']}**  ({quiz['type']})")
        
        # 이미지 슬라이더/갤러리
        images = quiz.get("images", [])
        if images:
            img_idx = st.session_state.quiz_img_idx % len(images)
            curr_img = images[img_idx]
            
            st.image(curr_img["url"], use_container_width=True)
            st.caption(f"📷 사진 설명: **{curr_img['caption']}** ({img_idx + 1} / {len(images)})")
            
            if len(images) > 1:
                btn_c1, btn_c2 = st.columns(2)
                with btn_c1:
                    if st.button("❮ 이전 사진 보기", key="prev_img"):
                        st.session_state.quiz_img_idx = (img_idx - 1) % len(images)
                        st.rerun()
                with btn_c2:
                    if st.button("다음 사진 보기 ❯", key="next_img"):
                        st.session_state.quiz_img_idx = (img_idx + 1) % len(images)
                        st.rerun()
        else:
            st.info("등록된 사진 자료가 없습니다.")

        # 피해 증상 설명
        symptom_text = quiz.get("symptoms") or quiz.get("damage_characteristics") or "상세 피해 사진을 참고하여 병명을 판별하시오."
        st.info(f"**[피해 증상 및 병징]**\n\n{symptom_text}")

        # 힌트 토글
        with st.expander("💡 힌트 보기 (학명 / 병원체 첫 글자)"):
            sci = quiz.get("scientific_or_en_name") or quiz.get("pathogen") or "학명 미기재"
            st.write(f"**학명:** `{sci}`")

    with col2:
        st.markdown("### ❓ 문제: 올바른 병해충명을 선택하세요.")
        
        choices = st.session_state.quiz_choices
        options_text = [f"{c['name']} (수목: {c['tree_name']})" for c in choices]
        
        # 4지선다 라디오 버튼
        selected = st.radio(
            "보기를 선택하세요:",
            options_text,
            index=None if not st.session_state.quiz_submitted else st.session_state.selected_choice,
            disabled=st.session_state.quiz_submitted
        )

        st.markdown("<br>", unsafe_allow_html=True)
        
        if not st.session_state.quiz_submitted:
            if st.button("✅ 정답 확인 & 에빙하우스 기록", type="primary", use_container_width=True):
                if selected is None:
                    st.warning("보기를 먼저 선택해 주세요!")
                else:
                    st.session_state.quiz_submitted = True
                    sel_idx = options_text.index(selected)
                    st.session_state.selected_choice = sel_idx
                    
                    chosen_item = choices[sel_idx]
                    is_correct = (chosen_item["id"] == quiz["id"])
                    
                    # 에빙하우스 상태 업데이트
                    st_data = st.session_state.eb_state[quiz["id"]]
                    if is_correct:
                        st_data["correct_count"] += 1
                        st_data["box"] = min(st_data["box"] + 1, 5)
                        days = EB_INTERVALS[st_data["box"] - 1]
                        st_data["next_review"] = time.time() + (days * 86400)
                    else:
                        st_data["wrong_count"] += 1
                        st_data["box"] = 1
                        st_data["next_review"] = time.time()
                    
                    st.rerun()
        else:
            sel_idx = st.session_state.selected_choice
            chosen_item = choices[sel_idx]
            is_correct = (chosen_item["id"] == quiz["id"])
            
            if is_correct:
                st.success(f"🎉 **정답입니다!** (Box {st.session_state.eb_state[quiz['id']]['box']} 단계로 승급)")
            else:
                st.error(f"❌ **오답입니다!** (내가 고른 답: {chosen_item['name']}) → **Box 1로 이동, 오늘 집중 복습**")

            # 상세 해설
            st.markdown(f"#### ▶ 정답: **{quiz['name']}** [{quiz['tree_name']}]")
            st.markdown(f"• **병원체/학명:** `{quiz.get('scientific_or_en_name') or quiz.get('pathogen') or '미기재'}`")
            
            control_txt = quiz.get("control_method") or "등록된 방제 정보 없음"
            st.markdown(f"• **핵심 방제 요령 (2차 실기 서술):**\n\n> {control_txt}")

            # AI 암기 팁
            mn = get_mnemonic_tip(quiz)
            st.info(f"**{mn['tag']}**\n\n{mn['tip']}")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🎲 다음 문제 풀기 ▶", type="primary", use_container_width=True):
                generate_new_quiz()
                st.rerun()

# ========================================================
# 화면 2: 전수 539종 도감 검색기
# ========================================================
elif mode == "📖 병해충 도감 검색 (전수 539종)":
    st.subheader("📖 수목 병해충 도감 전수 검색기 (539종)")
    
    # 필터
    f_c1, f_c2, f_c3 = st.columns([2, 1, 1])
    with f_c1:
        kw = st.text_input("🔍 검색어 (수목명, 병해충명, 증상, 학명, 약제명 등)", "")
    with f_c2:
        cat_filter = st.selectbox("대분류 필터", ["전체", "침엽수", "낙엽활엽수", "상록활엽수 · 대나무"])
    with f_c3:
        type_filter = st.selectbox("구분 필터", ["전체", "병해", "해충", "비전염성 피해/기타"])

    # 데이터 필터링
    filtered = []
    kw_lower = kw.strip().lower()
    for it in ALL_ITEMS:
        if cat_filter != "전체" and it["category"] != cat_filter:
            continue
        if type_filter != "전체" and it["type"] != type_filter:
            continue
        if kw_lower:
            text_blob = f"{it['name']} {it['tree_name']} {it.get('scientific_or_en_name','')} {it.get('symptoms','')} {it.get('control_method','')}".lower()
            if kw_lower not in text_blob:
                continue
        filtered.append(it)

    st.write(f"검색 결과: 총 **{len(filtered)}**건")
    st.markdown("---")

    # 카드 그리드 렌더링 (3열)
    cols = st.columns(3)
    for idx, item in enumerate(filtered[:60]): # 상위 60개 렌더링
        with cols[idx % 3]:
            with st.container(border=True):
                # 대표 썸네일
                imgs = item.get("images", [])
                if imgs:
                    st.image(imgs[0]["url"], use_container_width=True)
                else:
                    st.caption("사진 없음")

                st.markdown(f"**[{item['tree_name']}] {item['name']}**")
                st.caption(f"{item['category']} | {item['type']}")
                
                sci = item.get("scientific_or_en_name") or item.get("pathogen")
                if sci:
                    st.markdown(f"*`{sci}`*")

                with st.expander("상세 정보 보기"):
                    if item.get("damage_characteristics"):
                        st.markdown(f"**● 피해 특징:**\n{item['damage_characteristics']}")
                    if item.get("symptoms"):
                        st.markdown(f"**● 피해 증상/병징:**\n{item['symptoms']}")
                    if item.get("control_method"):
                        st.markdown(f"**● 방제 방법:**\n{item['control_method']}")
                    
                    mn = get_mnemonic_tip(item)
                    st.info(f"**{mn['tag']}**\n{mn['tip']}")
