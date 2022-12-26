##define coding=pypp

!include examples/rusty.h

fn main() {
    let number = 42;

    if number > 143 {
        panic!("oh no!");
    } else {
        println!("oh yes!");
    }
}
