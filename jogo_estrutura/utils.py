import os
import time

def custom_sleep(duration: int):
    if os.getenv("RUNNING_TESTS") != "1":
        time.sleep(duration)
        
def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')