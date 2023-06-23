from typing import Dict, List, Optional, TypeVar, Generic, Union
from pydantic import BaseModel, validator

T = TypeVar("T")

class Pagination(Generic[T], BaseModel):
    results: List[T]
    total_pages: int
    page: int
    page_size: int
    total: int
    next_page: Optional[str]
    previous_page: Optional[str]

    def __init__(
        self,
        values: List[T],
        page: int,
        total: int,
        total_pages: int,
        resource_url: str,
        request_filters: Optional[Dict[str, Union[str, int]]] = None,
        page_size: Optional[int] = None,
    ):
        page_size = page_size if page_size is not None else len(values)
        # Regenerate the query string
        filters = "&".join([f"{k}={v}" for k, v in request_filters.items()]) if request_filters else ""
        
        if page == total_pages:
            next_page = None
        else:
            next_page = f"{resource_url}?page={page+1}&page_size={page_size}"
            next_page += f"&{filters}" if filters else ""
        
        if page == 1:
            previous_page = None
        else:
            previous_page = f"{resource_url}?page={page-1}&page_size={page_size}"
            previous_page += f"&{filters}" if filters else ""

        super().__init__(
            results=values,
            total_pages=total_pages,
            page=page,
            page_size=page_size,
            total=total,
            next_page=next_page,
            previous_page=previous_page,
        )
    
    @validator("total_pages")
    def validate_total_pages(cls, total_pages):
        if total_pages < 1:
            raise ValueError("Invalid total number of pages")
        return total_pages

    @validator("page")
    def validate_page(cls, page, values):
        if page < 1:
            raise ValueError("Invalid page number")
        if "total_pages" in values and page > values["total_pages"]:
            raise ValueError("Page number out of range")
        return page
        
    @validator("page_size")
    def validate_page_size(cls, page_size, values):
        if page_size < 1:
            raise ValueError("Invalid page size")
        if "results" in values:
            if page_size < len(values["results"]):
                raise ValueError("Page size is too small to fit the results")
            if "page" in values and "total_pages" in values:
                if values["page"] < values["total_pages"] and page_size != len(values["results"]):
                    raise ValueError("Page is not full despite not being the last page")
        return page_size
        
    @validator("total")
    def validate_total(cls, total, values):
        if total < 0:
            raise ValueError("Invalid total")
        if "results" in values and total < len(values["results"]):
            raise ValueError("Total is less than the given results")
        if "total_pages" in values and "page_size" in values:
            if total > (values["total_pages"] * values["page_size"]):
                raise ValueError("Page size and total pages cannot fit the total content")
        return total
    