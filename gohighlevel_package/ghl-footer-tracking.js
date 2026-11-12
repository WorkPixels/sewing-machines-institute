/* GoHighLevel Footer Tracking Code for Sewing Machines Institute */
function switchProgramTab(tabKey) {
  var panels = document.querySelectorAll('.tab-panel');
  var buttons = document.querySelectorAll('.tab-btn');
  panels.forEach(function(p) { p.classList.remove('active'); });
  buttons.forEach(function(b) { b.classList.remove('active'); });

  var targetPanel = document.getElementById('tab-panel-' + tabKey);
  if (targetPanel) targetPanel.classList.add('active');

  if (window.event && window.event.currentTarget) {
    window.event.currentTarget.classList.add('active');
  }
}

function toggleFaq(element) {
  var item = element.parentElement;
  item.classList.toggle('active');
}

function updateCalculator() {
  var slider = document.getElementById('machineRange');
  if (!slider) return;
  var count = parseInt(slider.value, 10);
  var label = document.getElementById('machineCountLabel');
  if (label) label.innerText = count;

  var ratePerMachine = 110;
  var weekly = count * ratePerMachine;
  var monthly = Math.round(weekly * 4.333);
  var annual = monthly * 12;

  var monthEl = document.getElementById('monthlyEarnings');
  var annualEl = document.getElementById('annualEarnings');
  if (monthEl) monthEl.innerText = '$' + monthly.toLocaleString();
  if (annualEl) annualEl.innerText = '$' + annual.toLocaleString();
}

document.addEventListener('DOMContentLoaded', function() {
  updateCalculator();
});