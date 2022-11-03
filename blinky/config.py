import os

from pydantic import BaseSettings

def get_home_dir():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    

class Matrix(BaseSettings):
    rows: int 
    chain_length: int 
    parallel: int
    hardware_mapping: str
    led_pwm_bits: int
    led_pwm_lsb_nanoseconds: int
    led_pwm_dither_bits: int
    brightness: int
    gpio_slowdown: int
    scan_mode: int
    

    class Config:
        # .env is in the root directory of the project. get path from the click context
        env_file = os.path.join(get_home_dir(), ".env")
        print(env_file)
        # env_file = ".env"
        # prefix of the environment variables, in this case it will be
        # `MATRIX_ROWS` instead of `rows`
        env_file_encoding = "utf-8"
        env_prefix = "MATRIX_"
        # env_file = ".env"

matrix = Matrix()