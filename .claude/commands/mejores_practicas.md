"""
Instrucciones para aplicar convenciones de Python 3.12 con Type Hints modernos

Estas instrucciones deben seguirse al formatear código Python para asegurar
compatibilidad con Python 3.12 y uso de las mejores prácticas de tipado.
"""

# REGLAS GENERALES DE TYPE HINTS PYTHON 3.12

# 1. USAR BUILT-IN GENERICS (PEP 585)
#  CORRECTO - Python 3.12
from collections.abc import Callable, Iterable, Mapping
from typing import Any, TypeVar, Generic, Protocol, overload

def process_items(items: list[str]) -> dict[str, int]:
    """Usar built-in generics en lugar de typing.List, typing.Dict"""
    pass

def get_mapping() -> dict[str, list[int]]:
    """Anidación de generics usando built-ins"""
    pass

# L INCORRECTO - Estilo antiguo
# from typing import List, Dict
# def process_items(items: List[str]) -> Dict[str, int]:

# 2. UNION TYPES CON PIPE OPERATOR (PEP 604)
#  CORRECTO - Python 3.12
def handle_value(value: str | int | None) -> bool:
    """Usar | para union types en lugar de Union"""
    pass

def get_optional_data() -> dict[str, Any] | None:
    """Optional usando | None"""
    pass

# L INCORRECTO - Estilo antiguo
# from typing import Union, Optional
# def handle_value(value: Union[str, int, None]) -> bool:
# def get_optional_data() -> Optional[Dict[str, Any]]:

# 3. GENERIC TYPE ALIASES CON 'type' STATEMENT (PEP 695)
#  CORRECTO - Python 3.12
type JsonData = dict[str, Any]
type StringList = list[str]
type UserCallback[T] = Callable[[T], bool]
type OptionalMapping[K, V] = dict[K, V] | None

# Para clases genéricas
class Repository[T]:
    def __init__(self) -> None:
        self._items: list[T] = []
    
    def add(self, item: T) -> None:
        self._items.append(item)
    
    def get_all(self) -> list[T]:
        return self._items.copy()

# L INCORRECTO - Estilo antiguo
# from typing import TypeAlias
# JsonData: TypeAlias = Dict[str, Any]
# T = TypeVar('T')
# class Repository(Generic[T]):

# 4. FUNCTION TYPE HINTS CON COLLECTIONS.ABC
#  CORRECTO - Python 3.12
from collections.abc import Iterator, Generator, AsyncIterator

def process_lines(file_path: str) -> Iterator[str]:
    """Usar collections.abc.Iterator"""
    with open(file_path) as f:
        for line in f:
            yield line.strip()

def data_generator() -> Generator[int, None, None]:
    """Generator con yield type, send type, return type"""
    for i in range(10):
        yield i

async def async_data() -> AsyncIterator[str]:
    """AsyncIterator para async generators"""
    for i in range(5):
        yield f"data_{i}"

# 5. PROTOCOL CLASSES PARA STRUCTURAL TYPING
#  CORRECTO - Python 3.12
class Drawable(Protocol):
    def draw(self) -> None: ...

class Serializable(Protocol):
    def serialize(self) -> dict[str, Any]: ...

def render_object(obj: Drawable) -> None:
    """Usar Protocol en lugar de ABC cuando sea apropiado"""
    obj.draw()

# 6. OVERLOAD PARA FUNCTION SIGNATURES
#  CORRECTO - Python 3.12
@overload
def get_data(key: str) -> str: ...

@overload
def get_data(key: str, default: int) -> str | int: ...

def get_data(key: str, default: Any = None) -> Any:
    """Implementación con overloads para diferentes signatures"""
    pass

# 7. SELF Y CLS TYPES
#  CORRECTO - Python 3.12
from typing import Self

class BaseModel:
    def clone(self) -> Self:
        """Usar Self para return type del mismo tipo"""
        return type(self)()
    
    @classmethod
    def create(cls) -> Self:
        """Self también funciona en classmethods"""
        return cls()

# 8. DATACLASSES CON TYPE HINTS
#  CORRECTO - Python 3.12
from dataclasses import dataclass, field

@dataclass
class User:
    name: str
    age: int
    email: str | None = None
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

# 9. CONSTANTES Y LITERALS
#  CORRECTO - Python 3.12
from typing import Literal, Final

type Status = Literal["active", "inactive", "pending"]
type Direction = Literal["up", "down", "left", "right"]

MAX_CONNECTIONS: Final[int] = 100
DEFAULT_CONFIG: Final[dict[str, Any]] = {"timeout": 30}

def set_status(status: Status) -> None:
    """Usar Literal para valores específicos"""
    pass

# 10. ANNOTATED TYPES PARA METADATA
#  CORRECTO - Python 3.12
from typing import Annotated

type PositiveInt = Annotated[int, "Must be positive"]
type EmailStr = Annotated[str, "Must be valid email format"]

def create_user(user_id: PositiveInt, email: EmailStr) -> User:
    """Usar Annotated para agregar metadata a tipos"""
    pass

# 11. ASYNC FUNCTION TYPES
#  CORRECTO - Python 3.12
from collections.abc import Awaitable, Coroutine

async def fetch_data(url: str) -> dict[str, Any]:
    """Async function returning dict"""
    pass

def get_async_handler() -> Callable[[str], Awaitable[dict[str, Any]]]:
    """Function returning async callable"""
    return fetch_data

# 12. DJANGO SPECIFIC PATTERNS
#  CORRECTO - Para Django con Python 3.12
from django.db import models
from django.http import HttpRequest, HttpResponse

class Article(models.Model):
    title: str = models.CharField(max_length=200)
    content: str = models.TextField()
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)

def article_view(request: HttpRequest, article_id: int) -> HttpResponse:
    """Django view con type hints modernos"""
    pass

# REGLAS DE APLICACIÓN PARA FORMATEAR CÓDIGO:

"""
1. REEMPLAZAR IMPORTS OBSOLETOS:
   - typing.List ’ list
   - typing.Dict ’ dict  
   - typing.Set ’ set
   - typing.Tuple ’ tuple
   - typing.Union ’ |
   - typing.Optional[T] ’ T | None

2. CONVERTIR TYPE ALIASES:
   - TypeAlias declarations ’ type statements
   - TypeVar con Generic ’ nueva sintaxis con []

3. ACTUALIZAR COLLECTIONS:
   - typing.Callable ’ collections.abc.Callable
   - typing.Iterator ’ collections.abc.Iterator
   - typing.Mapping ’ collections.abc.Mapping

4. MODERNIZAR GENERICS:
   - class MyClass(Generic[T]) ’ class MyClass[T]
   - Eliminar TypeVar cuando sea posible

5. UNION TYPES:
   - Union[A, B] ’ A | B
   - Optional[T] ’ T | None

6. MANTENER COMPATIBILIDAD:
   - Solo aplicar si el proyecto usa Python 3.12+
   - Verificar que no hay uso de typing_extensions
"""