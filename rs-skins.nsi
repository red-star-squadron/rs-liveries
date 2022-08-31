; rs-skins.nsi


;--------------------------------

; This might help with large installs
FileBufSize 256

; Let's compress as much as possible. /GLOBAL breaks the installer. Too many big files!
SetCompressor /FINAL lzma

; LZMA compression only
SetCompressorDictSize 128


; The name of the installer
Name "RS Skins"
VIProductVersion ${VERSION}

; The file to write
OutFile "RS Skins.exe"

; Request application privileges for Windows Vista
RequestExecutionLevel user

; Build Unicode installer
Unicode True

; The default installation directory
InstallDir "$PROFILE\Saved Games\DCS.openbeta\Liveries"

;--------------------------------

; Pages
Page components
Page directory
Page instfiles

;--------------------------------

; Old and unused skin folder names are OK to remain in the cleanup list. We want to reduce clutter for the user
Section "Delete Red Star skins"
  RMDir /r "$INSTDIR\mig-29a\RED STAR MiG-29A"
  RMDir /r "$INSTDIR\mig-29g\RED STAR MiG-29G"
  RMDir /r "$INSTDIR\mig-29s\RED STAR MiG-29S"
  RMDir /r "$INSTDIR\su-27\RED STAR SU-27"
  RMDir /r "$INSTDIR\j-11a\RED STAR J-11A"
  RMDir /r "$INSTDIR\jf-17\RED STAR JF-17"
  RMDir /r "$INSTDIR\f-15c\RED STAR F15C"
  RMDir /r "$INSTDIR\f-16c_50\RED STAR F-16C_50"
  RMDir /r "$INSTDIR\fa-18c_hornet\RED STAR FA-18C"
SectionEnd

; Old and unused skin folder names are OK to remain in the cleanup list. We want to reduce clutter for the user
Section "Delete Red Star BLACK SQUADRON skins"
  RMDir /r "$INSTDIR\mig-21bis\RED STAR MiG-21 BLACK SQUADRON"
  RMDir /r "$INSTDIR\mig-29a\RED STAR MiG-29A BLACK SQUADRON"
  RMDir /r "$INSTDIR\mig-29g\RED STAR MiG-29G BLACK SQUADRON"
  RMDir /r "$INSTDIR\mig-29s\RED STAR MiG-29S BLACK SQUADRON"
  RMDir /r "$INSTDIR\su-27\RED STAR SU-27 BLACK SQUADRON"
  RMDir /r "$INSTDIR\j-11a\RED STAR J-11A BLACK SQUADRON"
  RMDir /r "$INSTDIR\jf-17\RED STAR JF-17 BLACK SQUADRON"
  RMDir /r "$INSTDIR\f-14a-135-gr\RED STAR F14A-135-GR BLACK SQUADRON"
  RMDir /r "$INSTDIR\f-14b\RED STAR F14B BLACK SQUADRON"
  RMDir /r "$INSTDIR\fa-15c\RED STAR F15C BLACK SQUADRON"
  RMDir /r "$INSTDIR\f-16c_50\RED STAR F-16C_50 BLACK SQUADRON"
  RMDir /r "$INSTDIR\fa-18c_hornet\RED STAR FA-18C BLACK SQUADRON"
SectionEnd

SectionGroup "Red Star"
  Section "MiG-29A"
    SetOutPath $INSTDIR\mig-29a
    File /r "mig-29a\RED STAR MiG-29A"
  SectionEnd
  Section "MiG-29G"
    SetOutPath $INSTDIR\mig-29g
    File /r "mig-29g\RED STAR MiG-29G"
  SectionEnd
  Section "MiG-29S"
    SetOutPath $INSTDIR\mig-29s
    File /r "mig-29s\RED STAR MiG-29S"
  SectionEnd
  Section "SU-27"
    SetOutPath $INSTDIR\su-27
    File /r "su-27\RED STAR SU-27"
  SectionEnd
  Section "J-11A"
    SetOutPath $INSTDIR\j-11a
    File /r "j-11a\RED STAR J-11A"
  SectionEnd
  Section "JF-17"
    SetOutPath $INSTDIR\jf-17
    File /r "jf-17\RED STAR JF-17"
  SectionEnd
  Section "F15C"
    SetOutPath $INSTDIR\f-15c
    File /r "f-15c\RED STAR F15C"
  SectionEnd
  Section "F-16C_50"
    SetOutPath $INSTDIR\f-16c_50
    File /r "f-16c_50\RED STAR F-16C_50"
  SectionEnd
  Section "FA-18C"
    SetOutPath $INSTDIR\fa-18c_hornet
    File /r "fa-18c_hornet\RED STAR FA-18C"
  SectionEnd
SectionGroupEnd



SectionGroup "Red Star BLACK SQUADRON"
  Section "MiG-21"
    SetOutPath $INSTDIR\mig-21bis
    File /r "mig-21bis\RED STAR MiG-21 BLACK SQUADRON"
  SectionEnd
  Section "MiG-29A"
    SetOutPath $INSTDIR\mig-29a
    File /r "mig-29a\RED STAR MiG-29A BLACK SQUADRON"
  SectionEnd
  Section "MiG-29G"
    SetOutPath $INSTDIR\mig-29g
    File /r "mig-29g\RED STAR MiG-29G BLACK SQUADRON"
  SectionEnd
  Section "MiG-29S"
    SetOutPath $INSTDIR\mig-29s
    File /r "mig-29s\RED STAR MiG-29S BLACK SQUADRON"
  SectionEnd
  Section "SU-27"
    SetOutPath $INSTDIR\su-27
    File /r "su-27\RED STAR SU-27 BLACK SQUADRON"
  SectionEnd
  Section "J-11A"
    SetOutPath $INSTDIR\j-11a
    File /r "j-11a\RED STAR J-11A BLACK SQUADRON"
  SectionEnd
  Section "JF-17"
    SetOutPath $INSTDIR\jf-17
    File /r "jf-17\RED STAR JF-17 BLACK SQUADRON"
  SectionEnd
  Section "F-14A-135-GR"
    SetOutPath $INSTDIR\f-14a-135-gr
    File /r "f-14a-135-gr\RED STAR F-14A-135-GR BLACK SQUADRON"
  SectionEnd
  Section "F-14B"
    SetOutPath $INSTDIR\f-14b
    File /r "f-14b\RED STAR F14-B BLACK SQUADRON"
  SectionEnd
  Section "F-15C"
    SetOutPath $INSTDIR\f-15c
    File /r "f-15c\RED STAR F15C BLACK SQUADRON"
  SectionEnd
  Section "F-16C_50"
    SetOutPath $INSTDIR\f-16c_50
    File /r "f-16c_50\RED STAR F-16C_50 BLACK SQUADRON"
  SectionEnd
  Section "FA-18C"
    SetOutPath $INSTDIR\fa-18c_hornet
    File /r "fa-18c_hornet\RED STAR FA-18C BLACK SQUADRON"
  SectionEnd
SectionGroupEnd
