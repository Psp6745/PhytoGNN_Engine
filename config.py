# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'phyto_gnn_secret_key_2026'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    MODEL_DIR = os.path.join(BASE_DIR, 'models')
    DEBUG = True