"""
このファイルは、Webアプリのメイン処理が記述されたファイルです。
"""

############################################################
# ライブラリの読み込み
############################################################
from dotenv import load_dotenv
load_dotenv()
import logging
import streamlit as st
import utils
from initialize import initialize
import components as cn  # display_product など
import components as cp  # display_stock_status_message 用（同一でもOK）
import constants as ct


############################################################
# 設定関連
############################################################
st.set_page_config(
    page_title=ct.APP_NAME
)

logger = logging.getLogger(ct.LOGGER_NAME)


############################################################
# 初期化処理
############################################################
print("✅ 初期化処理開始")
try:
    initialize()
    print("✅ 初期化処理成功")
except Exception as e:
    print(f"❌ 初期化エラー: {e}")
    logger.error(f"{ct.INITIALIZE_ERROR_MESSAGE}\n{e}")
    st.error(utils.build_error_message(ct.INITIALIZE_ERROR_MESSAGE), icon=ct.ERROR_ICON)
    st.stop()

# アプリ起動時のログ出力
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    logger.info(ct.APP_BOOT_MESSAGE)
    print("✅ アプリ初期化フラグ設定完了")

############################################################
# 初期表示
############################################################
# タイトル表示
cn.display_app_title()

# AIメッセージの初期表示
cn.display_initial_ai_message()


############################################################
# 会話ログの表示
############################################################
try:
    cn.display_conversation_log()
except Exception as e:
    logger.error(f"{ct.CONVERSATION_LOG_ERROR_MESSAGE}\n{e}")
    st.error(utils.build_error_message(ct.CONVERSATION_LOG_ERROR_MESSAGE))
    st.stop()


############################################################
# チャット入力の受け付け
############################################################
chat_message = st.chat_input(ct.CHAT_INPUT_HELPER_TEXT)


############################################################
# チャット送信時の処理
############################################################
if chat_message:
    # ==========================================
    # 1. ユーザーメッセージの表示
    # ==========================================
    logger.info({"message": chat_message})

    with st.chat_message("user", avatar=ct.USER_ICON_FILE_PATH):
        st.markdown(chat_message)

    # ==========================================
    # 2. LLMからの回答取得
    # ==========================================
    res_box = st.empty()
    with st.spinner(ct.SPINNER_TEXT):
        try:
            result = st.session_state.retriever.invoke(chat_message)
        except Exception as e:
            logger.error(f"{ct.RECOMMEND_ERROR_MESSAGE}\n{e}")
            st.error(utils.build_error_message(ct.RECOMMEND_ERROR_MESSAGE))
            st.stop()
    
    # ==========================================
    # 3. LLMからの回答表示
    # ==========================================
    with st.chat_message("assistant", avatar=ct.AI_ICON_FILE_PATH):
        try:
            cn.display_product(result)
            logger.info({"message": result})
        except Exception as e:
            logger.error(f"{ct.LLM_RESPONSE_DISP_ERROR_MESSAGE}\n{e}")
            st.error(utils.build_error_message(ct.LLM_RESPONSE_DISP_ERROR_MESSAGE))
            st.stop()

    # ==========================================
    # 4. 会話ログへの追加
    # ==========================================
    st.session_state.messages.append({"role": "user", "content": chat_message})
    st.session_state.messages.append({"role": "assistant", "content": result})


############################################################
# ✅ （任意）デモ用：在庫表示機能の単体テスト
############################################################
# ※ 通常運用では不要。表示テスト用コード
with st.expander("🔍 在庫表示の動作確認デモ（テスト用）", expanded=False):
    demo_product = {
        "商品ID": 24,
        "商品名": "USB充電式卓上加湿器『モイストミニ』",
        "価格": 2980,
        "stock_status": "なし"  # ← 残りわずか／あり に変更してテスト可
    }

    st.write(f"商品名：{demo_product['商品名']}（商品ID: {demo_product['商品ID']}）")
    st.write(f"価格：{demo_product['価格']}円")
    cp.display_stock_status_message(demo_product["stock_status"])