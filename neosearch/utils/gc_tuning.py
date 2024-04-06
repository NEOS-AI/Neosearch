import gc


def get_current_gc_threshold():
    return gc.get_threshold()


def gc_optimization_on_startup(debug:bool=False, disable_gc:bool=False):
    if debug:
        # gc.DEBUG_STATS: print statistics
        # gc.DEBUG_LEAK: print objects that are likely to be leaked
        # gc.DEBUG_UNCOLLECTABLE: print objects that cannot be collected
        gc.set_debug(gc.DEBUG_STATS | gc.DEBUG_LEAK | gc.DEBUG_UNCOLLECTABLE)

    if disable_gc:
        gc.disable()
        return

    # numpy나 torch는 import를 통해 초기화 시, 내부적으로 많은 object를 생성한다.
    # 이러한 object들이 reference count에 영향을 주고, gc가 더 자주 동작하도록 만든다.
    gc.freeze()

    # gc가 너무 자주 불리는 것도 문제가 될 수 있음.
    gc.set_threshold(80_000, 20, 20)
