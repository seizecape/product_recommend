"""
このファイルは、画面表示以外の様々な関数定義のファイルです。
"""

############################################################
# ライブラリの読み込み
############################################################
import os
from dotenv import load_dotenv
import streamlit as st
import logging
import sys
import unicodedata
import pandas as pd
import random  # stock_status 用
from langchain_community.document_loaders import PyMuPDFLoader, Docx2txtLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain.schema import HumanMessage, AIMessage
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from typing import List
from sudachipy import tokenizer, dictionary
from langchain_community.agent_toolkits import SlackToolkit
from langchain.agents import AgentType, initialize_agent
from langchain_community.document_loaders.csv_loader import CSVLoader


############################################################
# 関数定義
############################################################

def assign_stock_status(csv_path: str, output_path: str = None):
    """
    製品データにstock_status列を追加して保存する。
    stock_statusはランダムに「あり」「残りわずか」「なし」のいずれかを割り当てる。

    Parameters:
        csv_path (str): 入力CSVファイルのパス。
        output_path (str): 出力ファイルのパス。指定しない場合は上書き保存。
    """
    df = pd.read_csv(csv_path)

    # すでに列がある場合は上書き
    stock_statuses = ["あり", "残りわずか", "なし"]
    df["stock_status"] = [random.choice(stock_statuses) for _ in range(len(df))]

    save_path = output_path if output_path else csv_path
    df.to_csv(save_path, index=False)

    print(f"✅ stock_status列を追加して保存しました: {save_path}")


def build_error_message(message: str) -> str:
    """
    エラーメッセージを装飾付きで返す
    """
    return f"❌ {message}"


def preprocess_func(text: str) -> str:
    """
    retriever向けのテキスト前処理関数
    必要に応じて文字種の正規化などを実施
    """
    return unicodedata.normalize("NFKC", text).lower().strip()
