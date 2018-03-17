(begin
    (define x 10)
    (let ([x 3] [y 5])
        (display (+ x y))
        (display (* x y)))
    (display x)

    (define (fb n)
        (if (< n 2)
            1
            (+ (fb (- n 1)) (fb (- n 2)))))
    (display (fb 6))

    (define f
        (lambda (a b) (/ a b)))
    (display (f 6.5 8.8)))
