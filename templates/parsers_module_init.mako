% for site, parser in site_parsers:
from .${site} import ${parser}
% endfor

__all__ = (
    % for _, parser in site_parsers:
    "${parser}",
    % endfor
)
