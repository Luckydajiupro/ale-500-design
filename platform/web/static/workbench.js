document.addEventListener('click', function (event) {
  const trigger = event.target.closest('[data-add-row]');
  if (!trigger) return;
  const table = document.getElementById(trigger.dataset.addRow);
  const template = document.querySelector('#' + trigger.dataset.addRow.replace('-rows', '-row-template'));
  if (!table || !template) return;
  table.querySelector('tbody').appendChild(template.content.cloneNode(true));
});
