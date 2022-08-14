# Field Types

Thanks to features provided by _click_ and especially _pydantic_ data definitions, clidantic supports a large amount of field types, from the standard library up to JSON inputs.

## Primitive types

Considering primitive, non-complex data types, the library supports the following:

- `str`: values accepted as is, parsed as simple text without further processing.
- `int`: tries to convert any given input into an integer through `int(value)`.
- `float`: similarly, tries to convert any given input into a floating point number through `float(value)`
- `bytes`: similar to strings, however in this case the underlying representation remains _bytes_.
- `bool`: by default, booleans are intended as _flag_ options. In this case any boolean `field` will have the corresponding CLI flag `--field/--no-field`.

Clidantic takes care of converting _pydantic_ field types into _click_ parameter types, so that the automatically generated description reamins as faithful as possible.
Bear in mind that _click_ types are exploited only for documentation purposes, the final type checking will be carried out by pydantic when it's not validated by _click_.
Moreover, more complex types will default to `str` in most cases.

Here's an example of script with primitive types:
```python  title="main.py" linenums="1" hl_lines="9-13"
{!examples/typing/primitive_types.py!}
```

The help will show the specific type required in input
```console
$ python primitives.py --help
> Usage: primitives.py [OPTIONS]
>
> Options:
>   --name TEXT         [required]
>   --count INTEGER     [required]
>   --amount FLOAT      [required]
>   --paid / --no-paid  [required]
>   --beep-bop BYTES    [required]
>   --help              Show this message and exit.
```

Data is validated before the actual execution. In case of failure, a meaningful message will be displayed:

```console
$ python primitives.py --count hello
> Usage: primitives.py [OPTIONS]
> Try 'primitive_types.py --help' for help.
>
> Error: Invalid value for '--count': 'hello' is not a valid integer.
```


## Complex types

Thanks to pydantic, a large amount of complex and composable field types can be exploited.
Currently, the complex types that have been tested through clidantic are the following:

### Standard Library Types

Generally speaking, non-typed complex types will default to strings unless specified otherwise.

- `list`: without specifying the internal type, _list_ fields will behave as _multiple_ options of string items.
With [Multiple Options](https://click.palletsprojects.com/en/8.1.x/options/#multiple-options), the parameter must be provided multiple times.
For instance, `python cli.py --add 1 --add 2` will result in a list `[1, 2]`.
- `tuple`: similar to lists, this will behave as an unbounded sequence of strings, with multiple parameters.
- `dict`: dictionaries are interpreted as JSON strings. In this case, there will be no further validation.
Given that valid JSON strings require double quotes, arguments provided through the command line must use single-quoted strings.
For instance, `python cli.py --extras '{"items": 12}'` will be successfully parsed, while `python cli.py --extras "{'items': 12}"` will not.
- `set`: again, from a command line point of view, sets are a simple list of values. In this case, repeated values will be excluded.
For instance, `python cli.py --add a --add b --add a` will result in a set `{'a', 'b'}`.
- `frozenset`: _frozen_ sets adopt the same behavior as normal sets, with the only difference that they remain immutable.
- `deque`: similarly, _deques_ act as sequences from a CLI standpoint, while being treaded as double-ended queues in code.

### Typing Containers


- `Any`: For obvious reasons, _Any_ fields will behave as `str` options without further processing.
- `Optional`: optional typing can be interpreted as _syntactic sugar_, meaning it will not have any effect on the underlying
validation, but it provides an explicit declaration that the field can also accept `None` as value.
For the CLI, `Optional` will automatically add a `None` default value to the field, indeed bahaving as an optional parameter.
- `List`: Similar to standard lists, typing _Lists_ behave as sequences of items. In this case however the inner type is
exploited to provide further validation through _pydantic_.
For instance, `python cli.py --add a --add b` will result in a validation error for a list of integers `List[int]`.
- `Tuple`: typing _Tuples_ can behave in two ways: when using a _variable length_ structure (i.e., `Tuple[int]` or `Tuple[int, ...]`),
tuples act as a sequence of typed items, validated through _pydantic, where the parameter is specified multiple times.
When using a _fixed length_ structure (i.e., `Tuple[int, int]` or similar), they are considered [multi-value options](https://click.palletsprojects.com/en/8.1.x/options/#tuples-as-multi-value-options),
 where the parameter is specified once, followed by the sequence of values separated by whitespaces.
 For instance . `python cli.py --items a b c` will results in a tuple `('a', 'b', 'c')`.
- `Dict`: Similar to the standard `dict` field, typing dictionaries require a JSON string as input. However, inner types
allow for a finer validation: for instance, considering a `metrics: Dict[str, float]` field, `--metrics '{"f1": 0.93}'` is accepted,
while `--metrics '{"auc": "a"}'` is not a valid input.
- `Deque`: with the same reasoning of typed lists and tuples, _Deques_ will act as sequences with a specific type.
- `Set`: As you guessed, typed sets act as multiple options where repeated items are excluded, with additional type validation
on the items themselves.
- `FrozenSet`: as with _Sets_, but they represent immutable structures after parsing.
- `Sequence`: with no surpise, sequences act as sequences, nothing to add here.

!!! warning

    for obvious reasons, `Union` typings are not supported at this time.
    Parsing a multi-valued parameter is really more of a phylosophical problem than a technical one.
    Future releases will consider the support for this typing.


The code below provides a relatively comprehensive view of most container types supported through _clidantic_.
The list is not exhaustive: broadly speaking, the logic for the parameter definition can be summarized as follows:

- _if_ it is any other complex supported type _then_ provide the specific type
- _if_ it is a container type _then_:
    - _if_ it has no inner type _then_ behave as sequence of strings
    - _if_ it has one inner type `T`, or `T` with ellipsis, behave as sequence of type `T`
    - _if_ it has 2+ inner types without ellipsis, behave as fixed-length sequence with the given list of types
- _else_ left _click_ attempt the type inference, worst case scenario will be `str`

```python  title="complex.py" linenums="1"
{!examples/typing/container_types.py!}
```

Executing this script with the _help_ command will provide the description for the current configuration.
There are a few things to notice here: when possible and specified, _clidantic_ will show the time of the item
accepted by the multi-option fields, otherwise it will appear as `TEXT`.
Also, defaults are allowed and validated: when optional or `None`, a more descriptive `(empty <TYPE>)` will inform
the user of the underlying iterable class.

```console
$ python complex.py --help
> Usage: complex.py [OPTIONS]
>
> Options:
>   --simple-list TEXT              [default: (empty list)]
>   --list-of-ints INTEGER          [default: (empty list)]
>   --simple-tuple TEXT             [default: (empty tuple)]
>   --multi-typed-tuple <INTEGER FLOAT TEXT BOOLEAN>...
>                                   [default: (empty tuple)]
>   --simple-dict JSON              [default: (empty dict)]
>   --dict-str-float JSON           [default: (empty dict)]
>   --simple-set TEXT               [default: (empty set)]
>   --set-bytes BYTES               [default: (empty set)]
>   --frozen-set INTEGER            [default: (empty frozenset)]
>   --none-or-str TEXT
>   --sequence-of-ints INTEGER      [default: (empty Sequence)]
>   --compound JSON                 [default: (empty dict)]
>   --deque INTEGER                 [default: (empty deque)]
>   --help                          Show this message and exit.
```

### Literals and Enums

Sometimes it may be useful to directly limit the choices of certain fields, by letting the user select among a fixed list of values.
In this case, _clidantic_ provides this feature using  _pydantic_'s support for `Enum` and `Literal` types, parsed from the command line
through _click_ `Choice` derivatives.

While _Enums_ represent the standard way to provide choice-based options, _Literals_ can be seen as a lightweight enumeration.
In general, the latter are simpler and easier to handle than the former for most use cases.
_Enums_ on the other hand provide both a `name` and a `value` component, where only the former is exploited for the parameter definition.
The latter can represent any kind of object, therefore making _enums_ more suitable for more complex use cases.

The following script presents a sample of possible choice definitions in _clidantic_:
```python  title="choices.py" linenums="1"
{!examples/typing/choice_types.py!}
```

!!! warning

    As you probably noticed, the string enumeration only subclasses `Enum`.
    Strictly speaking, `ToolEnum(str, Enum)` would be a better inheritance definition, however this breaks the type
    inference by providing two origins.

    Currently, there are two solutions:

    - **simply use Enum**, it should be fine in most cases.
    - **use StrEnum**, which however is only available since Python 3.11.

Launching the help for this script will result in the following output:
```console
$ python choices.py --help
> Usage: choices.py [OPTIONS]
>
> Options:
>   --a [one|two]                   [required]
>   --b [1|2]                       [default: 2]
>   --c [True|False]                [required]
>   --d [hammer|screwdriver]        [required]
>   --e [ok|not_found|interal_error]
>                                   [default: not_found]
>   --help                          Show this message and exit.
```

You can notice that, even without explicit description, choice-based fields will automatically provide the list of possible values.
Defaults also behave as expected: both literals and enums will accept any of the allowed values as default, and it that
case the selected item will be displayed as _default_ in the console.
Again, note that the `name` field enum-based choice parameters is handled by the CLI, not its actual value.

### Module Types
For peculiar use cases, where the aim is to dinamically import a specific module, fields can be annotated with the `Type` _type_ for module-like parameters.
Specifying `field: Type[T]`, _pydantic_ will ensure that `field` will assume as values only classes (not instances) that are subclasses of `T`.

!!! note

    Support for module types is still experimental at this point.

Here's an example of module type definition:
```python  title="modules.py" linenums="1"
{!examples/typing/module_types.py!}
```

Again, the help command will results in the following output:
```console
$ python modules.py --help
> Usage: modules.py [OPTIONS]
>
> Options:
>   --field MODULE  [default: __main__.SGD]
>   --help          Show this message and exit.
```
The example is meant to be a contained, working example, however it is not recommended to place both the CLI instance
and the modules to be selected in the same script, as Python's weird importing and execution mechanisms may become a problem.
For instance, it this case the default `modules.SGD` class appears to belong to the `__main__` module.
This is in fact the name that Python will set on the top-level _entry point_, regardless of the script name.

Nevertheless, module types basically require an _import_ path to the correct _module_ (not file), which in this case corresponds to `__main__`.
So, if we run `python module_types.py --field __main__.Adam`, we will obtain the correct assignment to the module field:

```console
$ python modules.py --field __main__.Adam
> <class '__main__.Adam'>
```

While wrong paths will of course result in an error, informing the user about the mistake:

```console
$ python modules.py --field myscript.MyClass
> Try 'modules.py --help' for help.
>
> Error: Invalid value for '--field': 'myscript.MyClass' is not a valid object (<class 'ModuleNotFoundError'>: No module named 'myscript')
```