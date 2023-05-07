@echo off

:MENU
cls
echo Welcome to AlexFlipnote/discord_bot.py
echo    1 Start the bot
echo    2 Install dependencies
echo    3 Exit menu
echo.

echo Type the number to choose an option and press enter
SET /P item="> "
cls

IF %item%==1 (
  GOTO START_BOT
) ELSE IF %item%==2 (
  GOTO UPDATE_PIP
) ELSE IF %item%==3 (
  GOTO EOF
) ELSE (
  GOTO MENU
)

:START_BOT
  python index.py
  pause
  GOTO EOF

:UPDATE_PIP
  where pip
  cls
  IF %ERRORLEVEL% NEQ 0 (
    ECHO You might need to install pip first or add it to your PATH
    pause
    exit
  )
  CALL pip install -r requirements.txt --upgrade
  pause
  GOTO MENU

:EOF
  exit
