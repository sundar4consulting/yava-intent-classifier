"""Watson Orchestrate Entry Point"""
from src.skill import main

def handler(params):
    return main(params)
