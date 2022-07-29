; rs-skins.nsi


;--------------------------------


; Let's compress as much as possible
SetCompressor /FINAL /SOLID lzma
SetCompressorDictSize 128


; The name of the installer
Name "RS Skins"

; The file to write
OutFile "RS Skins.exe"

; Request application privileges for Windows Vista
RequestExecutionLevel user

; Build Unicode installer
Unicode True

; The default installation directory
InstallDir "$PROFILE\Saved Games\DCS\Liveries"

;--------------------------------

; Pages
Page components
Page directory
Page instfiles

;--------------------------------

; Old and unused skin folder names are OK to remain in the cleanup list. We want to reduce clutter for the user
Section "Clean old Red Star skins"
  RMDir /r "$INSTDIR\mig-29s\RED STAR MiG-29S"
  RMDir /r "$INSTDIR\mig-29a\RED STAR MiG-29A"
  RMDir /r "$INSTDIR\mig-29g\RED STAR MiG-29G"
  RMDir /r "$INSTDIR\jf-17\RED STAR JF-17"
  RMDir /r "$INSTDIR\j-11a\RED STAR J-11A"
  RMDir /r "$INSTDIR\su-27\RED STAR SU-27"
  RMDir /r "$INSTDIR\f-16c_50\RED STAR F-16C_50"
  RMDir /r "$INSTDIR\fa-18c_hornet\RED STAR FA-18C"
  RMDir /r "$INSTDIR\f-15c\RED STAR F15C"
SectionEnd

; Old and unused skin folder names are OK to remain in the cleanup list. We want to reduce clutter for the user
Section "Clean old Red Star BLACK SQUADRON skins"
  RMDir /r "$INSTDIR\mig-21bis\RED STAR MiG-21 BLACK SQUADRON"
  RMDir /r "$INSTDIR\mig-29s\RED STAR MiG-29S BLACK SQUADRON"
  RMDir /r "$INSTDIR\mig-29a\RED STAR MiG-29A BLACK SQUADRON"
  RMDir /r "$INSTDIR\mig-29g\RED STAR MiG-29G BLACK SQUADRON"
  RMDir /r "$INSTDIR\f-16c_50\RED STAR F-16C_50 BLACK SQUADRON"
  RMDir /r "$INSTDIR\j-11a\RED STAR J-11A BLACK SQUADRON"
  RMDir /r "$INSTDIR\su-27\RED STAR SU-27 BLACK SQUADRON"
  RMDir /r "$INSTDIR\fa-18c_hornet\RED STAR FA-18C BLACK SQUADRON"
SectionEnd

Section "Red Star"
  SetOutPath $INSTDIR\mig-29s
  File /r "mig-29s\RED STAR MiG-29S"
  SetOutPath $INSTDIR\mig-29a
  File /r "mig-29a\RED STAR MiG-29A"
  SetOutPath $INSTDIR\mig-29g
  File /r "mig-29g\RED STAR MiG-29G"
  SetOutPath $INSTDIR\jf-17
  File /r "jf-17\RED STAR JF-17"
  SetOutPath $INSTDIR\j-11a
  File /r "j-11a\RED STAR J-11A"
  SetOutPath $INSTDIR\su-27
  File /r "su-27\RED STAR SU-27"
  SetOutPath $INSTDIR\f-16c_50
  File /r "f-16c_50\RED STAR F-16C_50"
  SetOutPath $INSTDIR\fa-18c_hornet
  File /r "fa-18c_hornet\RED STAR FA-18C"
  SetOutPath $INSTDIR\f-15c
  File /r "f-15c\RED STAR F15C"
SectionEnd


Section "Red Star BLACK SQUADRON"
  SetOutPath $INSTDIR\mig-21bis
  File /r "mig-21bis\RED STAR MiG-21 BLACK SQUADRON"
  SetOutPath $INSTDIR\mig-29s
  File /r "mig-29s\RED STAR MiG-29S BLACK SQUADRON"
  SetOutPath $INSTDIR\mig-29a
  File /r "mig-29a\RED STAR MiG-29A BLACK SQUADRON"
  SetOutPath $INSTDIR\mig-29g
  File /r "mig-29g\RED STAR MiG-29G BLACK SQUADRON"
  SetOutPath $INSTDIR\f-16c_50
  File /r "f-16c_50\RED STAR F-16C_50 BLACK SQUADRON"
  SetOutPath $INSTDIR\j-11a
  File /r "j-11a\RED STAR J-11A BLACK SQUADRON"
  SetOutPath $INSTDIR\su-27
  File /r "su-27\RED STAR SU-27 BLACK SQUADRON"
  SetOutPath $INSTDIR\fa-18c_hornet
  File /r "fa-18c_hornet\RED STAR FA-18C BLACK SQUADRON"
SectionEnd
