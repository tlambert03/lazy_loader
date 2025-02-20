![PyPI](https://img.shields.io/pypi/v/lazy-loader?style=for-the-badge)

`lazy-loader` makes it easy to load subpackages and functions on demand.

## Motivation

1. Allow subpackages to be made visible to users without incurring import costs.
2. Allow external libraries to be imported only when used, improving import times.

For a more detailed discussion, see [the SPEC](https://scientific-python.org/specs/spec-0001/).

## Installation

```
pip install -U lazy-loader
```

## Usage

### Lazily load subpackages

Consider the `__init__.py` from [scikit-image](https://scikit-image.org):

```python
subpackages = [
    ...,
    'filters',
    ...
]

import lazy_loader as lazy
__getattr__, __dir__, _ = lazy.attach(__name__, subpackages)
```

You can now do:

```python
import skimage as ski
ski.filters.gaussian(...)
```

The `filters` subpackages will only be loaded once accessed.

### Lazily load subpackages and functions

Consider `skimage/filters/__init__.py`:

```python
from ..util import lazy

__getattr__, __dir__, __all__ = lazy.attach(
    __name__,
    submodules=['rank'],
    submod_attrs={
        '_gaussian': ['gaussian', 'difference_of_gaussians'],
        'edges': ['sobel', 'scharr', 'prewitt', 'roberts',
                  'laplace', 'farid']
    }
)
```

The above is equivalent to:

```python
from . import rank
from ._gaussian import gaussian, difference_of_gaussians
from .edges import (sobel, scharr, prewitt, roberts,
                    laplace, farid)
```

Except that all subpackages (such as `rank`) and functions (such as `sobel`) are loaded upon access.

### Early failure

With lazy loading, missing imports no longer fail upon loading the
library.  During development and testing, you can set the `EAGER_IMPORT`
environment variable to disable lazy loading.

### External libraries

The `lazy.attach` function discussed above is used to set up package
internal imports.

Use `lazy.load` to lazily import external libraries:

```python
linalg = lazy.load('scipy.linalg')  # `linalg` will only be loaded when accessed
```

You can also ask `lazy.load` to raise import errors as soon as it is called:

```
linalg = lazy.load('scipy.linalg', error_on_import=True)
```
