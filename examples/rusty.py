##define coding=pypp

!define { :?NEWLINE?INDENT
!define } ?NEWLINE?DEDENT
!define fn def
!define let
!define `println!` print
!define `panic!` raise SystemExit
!define ?ENDMARKER main()?ENDMARKER

fn main() {
    let number = 42;

    if number > 143 {
        panic!("oh no!");
    } else {
        println!("oh yes!");
    }
}
