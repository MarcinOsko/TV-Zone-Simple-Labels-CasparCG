#!/bin/sh

create-dmg \
  --volname "Simple Labels for CasparCG" \
  --volicon "SA_logo_diskimege_SL.icns" \
  --background "pic.png" \
  --eula "EULA.txt" \
  --add-file "Templates" "Templates" 500 230 \
  --add-file "README.txt" "README.md" 500 70 \
  --add-file "EULA.txt" "EULA.txt" 630 70 \
  --window-pos 200 200 \
  --text-size 15 \
  --window-size 720 360 \
  --icon-size 120 \
  --icon "Simple Labels for CasparCG.app" 110 150 \
  --hide-extension "Simple Labels for CasparCG.app" \
  --app-drop-link 290 150 \
  --no-internet-enable \
  "dist/Simple Labels for CasparCG.dmg" \
  "dist/dmg/"