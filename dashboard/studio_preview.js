/* Small, scheme-checked renderer for actual student answer previews. */
(function (root, factory) {
  var renderer = factory();
  if (typeof module === 'object' && module.exports) module.exports = renderer;
  else root.StudioPreview = renderer;
}(typeof window === 'undefined' ? this : window, function () {
  'use strict';
  function escape(value) {
    return String(value || '').replace(/[&<>"']/g, function (character) {
      return {'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'}[character];
    });
  }
  function link(label, url) {
    if (!/^https?:\/\//i.test(url)) return escape(label + ' (' + url + ')');
    return '<a href="' + escape(url) + '" target="_blank" rel="noopener noreferrer">' + escape(label) + '</a>';
  }
  function inline(text) {
    var expression = /\[([^\]\n]+)\]\(([^\s)]+)\)|https?:\/\/[^\s<>]+|\*\*([^*]+)\*\*/g;
    var output = '', previous = 0, match;
    while ((match = expression.exec(text))) {
      output += escape(text.slice(previous, match.index));
      if (match[1]) output += link(match[1], match[2]);
      else if (match[3]) output += '<strong>' + escape(match[3]) + '</strong>';
      else {
        var url = match[0].replace(/[.,;!?)]+$/, '');
        var label = url.length > 80 ? 'Open official link' : url;
        output += link(label, url) + escape(match[0].slice(url.length));
      }
      previous = expression.lastIndex;
    }
    return output + escape(text.slice(previous));
  }
  return {render: function (text) { return String(text || '').split('\n').map(inline).join('<br>'); }};
}));
