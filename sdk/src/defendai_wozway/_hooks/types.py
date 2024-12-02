

from abc import ABC, abstractmethod
from defendai_wozway.httpclient import HttpClient
import httpx
from typing import Any, Callable, List, Optional, Tuple, Union


class HookContext:
    operation_id: str
    oauth2_scopes: Optional[List[str]] = None
    security_source: Optional[Union[Any, Callable[[], Any]]] = None

    def __init__(
        self,
        operation_id: str,
        oauth2_scopes: Optional[List[str]],
        security_source: Optional[Union[Any, Callable[[], Any]]],
    ):
        self.operation_id = operation_id
        self.oauth2_scopes = oauth2_scopes
        self.security_source = security_source


class BeforeRequestContext(HookContext):
    def __init__(self, hook_ctx: HookContext):
        super().__init__(
            hook_ctx.operation_id, hook_ctx.oauth2_scopes, hook_ctx.security_source
        )


class AfterSuccessContext(HookContext):
    def __init__(self, hook_ctx: HookContext):
        super().__init__(
            hook_ctx.operation_id, hook_ctx.oauth2_scopes, hook_ctx.security_source
        )


class AfterErrorContext(HookContext):
    def __init__(self, hook_ctx: HookContext):
        super().__init__(
            hook_ctx.operation_id, hook_ctx.oauth2_scopes, hook_ctx.security_source
        )


class SDKInitHook(ABC):
    @abstractmethod
    def sdk_init(self, base_url: str, client: HttpClient) -> Tuple[str, HttpClient]:
        pass


class BeforeRequestHook(ABC):
    @abstractmethod
    def before_request(
        self, hook_ctx: BeforeRequestContext, request: httpx.Request
    ) -> Union[httpx.Request, Exception]:
        pass


class AfterSuccessHook(ABC):
    @abstractmethod
    def after_success(
        self, hook_ctx: AfterSuccessContext, response: httpx.Response
    ) -> Union[httpx.Response, Exception]:
        pass


class AfterErrorHook(ABC):
    @abstractmethod
    def after_error(
        self,
        hook_ctx: AfterErrorContext,
        response: Optional[httpx.Response],
        error: Optional[Exception],
    ) -> Union[Tuple[Optional[httpx.Response], Optional[Exception]], Exception]:
        pass


class Hooks(ABC):
    @abstractmethod
    def register_sdk_init_hook(self, hook: SDKInitHook):
        pass

    @abstractmethod
    def register_before_request_hook(self, hook: BeforeRequestHook):
        pass

    @abstractmethod
    def register_after_success_hook(self, hook: AfterSuccessHook):
        pass

    @abstractmethod
    def register_after_error_hook(self, hook: AfterErrorHook):
        pass
