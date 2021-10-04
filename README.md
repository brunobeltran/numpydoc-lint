# Numpydoc Linting

No tool seemed to exist to run numpydoc.validate inside of flake, so I went
ahead and made a numpydoc wrapper myself that recursive traverses a package,
uses inspect.getmembers along with the properties of inspect.getmodule to get
all functions/methods/(and other things with docstrings) defined in a module,
and passes them all to numpydoc.validate for testing.
