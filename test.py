class QMessageBox:
    StandardButton = 0

class StandardButton(object):
    ButtonMask               : QMessageBox.StandardButton = ... # -0x301
    NoButton                 : QMessageBox.StandardButton = ... # 0x0
    Default                  : QMessageBox.StandardButton = ... # 0x100
    Escape                   : QMessageBox.StandardButton = ... # 0x200
    FlagMask                 : QMessageBox.StandardButton = ... # 0x300
    FirstButton              : QMessageBox.StandardButton = ... # 0x400
    Ok                       : QMessageBox.StandardButton = ... # 0x400
    Save                     : QMessageBox.StandardButton = ... # 0x800
    SaveAll                  : QMessageBox.StandardButton = ... # 0x1000
    Open                     : QMessageBox.StandardButton = ... # 0x2000
    Yes                      : QMessageBox.StandardButton = ... # 0x4000
    YesAll                   : QMessageBox.StandardButton = ... # 0x8000
    YesToAll                 : QMessageBox.StandardButton = ... # 0x8000
    No                       : QMessageBox.StandardButton = ... # 0x10000
    NoAll                    : QMessageBox.StandardButton = ... # 0x20000
    NoToAll                  : QMessageBox.StandardButton = ... # 0x20000
    Abort                    : QMessageBox.StandardButton = ... # 0x40000
    Retry                    : QMessageBox.StandardButton = ... # 0x80000
    Ignore                   : QMessageBox.StandardButton = ... # 0x100000
    Close                    : QMessageBox.StandardButton = ... # 0x200000
    Cancel                   : QMessageBox.StandardButton = ... # 0x400000
    Discard                  : QMessageBox.StandardButton = ... # 0x800000
    Help                     : QMessageBox.StandardButton = ... # 0x1000000
    Apply                    : QMessageBox.StandardButton = ... # 0x2000000
    Reset                    : QMessageBox.StandardButton = ... # 0x4000000
    LastButton               : QMessageBox.StandardButton = ... # 0x8000000
    RestoreDefaults          : QMessageBox.StandardButton = ... # 0x8000000

class TestClass(object):
    Close : 123 = 123


sb = StandardButton()
#t = TestClass()
print(sb.ButtonMask)
#print(t.Close)
print(...)
print(type(...))



#print(dir(__builtins__))