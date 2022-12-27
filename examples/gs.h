c = [
!define , lambda: a[:-1] + [len(a[-1])],
!define . lambda: a + [a[-1]],
!define @ lambda: a[:-3] + [a[-2], a[-1], a[-3]],
!define p lambda: (print(a[-1]), a[:-1])[-1],
!define + lambda: a[:-2] + [a[-1] + a[-2]],
!define ; lambda: a[:-1],
!define * lambda: (globals().__setitem__("c", a[-1] * a[-2] + c), a[:-2])[-1],
!define ?NUMBER ?0,
!define { [
!define } ],
!define ?ENDMARKER ];a=[[]]?NEWLINE while c: x=c.pop(0); a = x() if callable(x) else a + [x]?ENDMARKER
