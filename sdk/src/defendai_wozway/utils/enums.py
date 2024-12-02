

import enum


class OpenEnumMeta(enum.EnumMeta):
    def __call__(
        cls, value, names=None, *, module=None, qualname=None, type=None, start=1
    ):
        # The `type` kwarg also happens to be a built-in that pylint flags as
        # redeclared. Safe to ignore this lint rule with this scope.
        # pylint: disable=redefined-builtin

        if names is not None:
            return super().__call__(
                value,
                names=names,
                module=module,
                qualname=qualname,
                type=type,
                start=start,
            )

        try:
            return super().__call__(
                value,
                names=names,  # pyright: ignore[reportArgumentType]
                module=module,
                qualname=qualname,
                type=type,
                start=start,
            )
        except ValueError:
            return value
