<div class="modal fade">
  <div class="modal-dialog" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
    <div class="modal-content">
      <form data-action="${request.custom_route_path('new_json')}">
    <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
        <h4 class="modal-title">New file</h4>
      </div>
      <div class="modal-body">
    <div class="form-group">
      <label>Choose a dtd:</label>
      <select data-href="${request.custom_route_path('get_tags_json')}" class="dtd-urls form-control" name="dtd-url">
      % for dtd_url in dtd_urls:
        <option value="${dtd_url}">${dtd_url}</option>
      % endfor
      </select>
    </div>
    <div class="form-group">
      <label>Choose a root tag</label>
      <select class="dtd-tags form-control" name="dtd-tag">
        % for tag in tags:
          <option value="${tag}">${tag}</option>
        % endfor
      </select>
    </div>
      </div>
      <div class="modal-footer">
        <a href="#" class="btn" data-dismiss="modal">Cancel</a>
        <button type="submit" class="btn btn-primary submit">Create</button>
      </div>
    </form>
  </div>
  </div>
</div>