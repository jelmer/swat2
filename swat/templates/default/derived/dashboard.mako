<%inherit file="/default/base/base.mako" />
<%namespace name="widget" file="/default/component/widget.mako" />

${widget.write_layout(c.layout)}

<%doc></%doc>
<%def name="page_title()">
    ${parent.page_title()} :: Dashboard
</%def>