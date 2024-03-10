# AutoGameBot (AGB)

The bot's work mainly consists of grabbing the system window with the game, processing images and emulating control signals based on certain logic.

I usually use [scrcpy](https://github.com/Genymobile/scrcpy) to broadcast images from Android and transfer control actions to the phone.

## Launch

```bash
python3 -m venv env
source /env/bin/activate
```

```sh
python -m venv env
env\Scripts\activate.bat
```

```sh
(env) pip install -r requirements.txt
```
