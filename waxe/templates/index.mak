<%inherit file="base.mak" />

% if error_msg:
  Error: ${error_msg|n}
% endif

<ul class="breadcrumb navbar-fixed-top" style="top: 55px; z-index: 999; background-color: transparent; margin-bottom: 0px; padding-top: 4px; padding-bottom: 2px;">
% if breadcrumb:
  ${breadcrumb|n}
% endif
</ul>

<div class="ui-layout-center">
  <div class="content">
    % if content:
	    ${content|n}
	  % endif
  </div>
</div>

<div class="ui-layout-east">
  <div id="tree-container">
    <div id="tree">Tree</div>
  </div>
</div>

% if jstree_data:
  <script>
	  var jstree_data = ${jstree_data|n};
  </script>
% endif
