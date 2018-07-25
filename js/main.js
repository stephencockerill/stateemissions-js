function initialize() {
  const earliest_year = '1980';
  const latest_year = '2014';
  addYearSelectOptions(earliest_year, latest_year);
}

function render() {
  year_selected = document.querySelector('#yearSelect').value
  getEmissionsData(year_selected);
  updateChartTitleYears(year_selected);
};

function getEmissionsData(year) {
  fetch('./data/all_states_emissions.json')
    .then(response => response.json())
    .then(data => {
      let emissions = filterByYear(data, year);
      addVerticalChartBars(emissions);
      addHorizontalChartBars(emissions);
    });
};

function filterByYear(data, year) {
  let maxValue = 0;
  let filtered = {
    'data': [],
    'sorted': [],
  };
  for (let state of Object.keys(data)) {
    let inserted = false;
    let value = data[state][year];
    maxValue = Math.max(value, maxValue)
    let stateObj = {
      'state': state,
      'year': year,
      'value': value,
    };
    for (let [index, entry] of filtered.sorted.entries()) {
      if (value < entry.value) {
        filtered.sorted.splice(index, 0, stateObj);
        inserted = true;
        break;
      };
    };
    if (!inserted) {
      filtered.sorted.push(stateObj);
    };
    filtered.data.push(stateObj);
  };
  filtered.maxValue = maxValue;
  return filtered;
};

function addVerticalChartBars(data) {

  let chart = document.querySelector('#verticalChart');
  // remove any existing bars
  removeChildren(chart);

  maxValue = data.maxValue;
  // get the ten greatest emitting states from the sorted list
  for (let state of data.sorted.slice(-10)) {
    // height of the bar is the percentage of the max value
    let height = (state.value / maxValue) * 100;

    // create bar element as a list item
    let bar = document.createElement('li');
    bar.classList.add('Chart__bar');
    bar.classList.add('Chart__bar--vertical');
    bar.setAttribute('year', state.year);
    bar.setAttribute('data-value', state.value);
    bar.style.height = height + '%';
    bar.onclick = barAlert;
    bar.textContent = state.state;

    // add bar to the chart 
    chart.appendChild(bar);
  };
};

function addHorizontalChartBars(data) {
  let chart = document.querySelector('#horizontalChart');
  // remove any existing bars
  removeChildren(chart);

  maxValue = data.maxValue;
  for (let state of data.data) {
    // width of the bar is the percentage of the max value
    let width = (state.value / maxValue) * 100;

    // create bar element as a list item
    let bar = document.createElement('li');
    bar.classList.add('Chart__bar');
    bar.classList.add('Chart__bar--horizontal');
    bar.setAttribute('year', state.year);
    bar.setAttribute('data-value', state.value);
    bar.style.width = width + '%';
    bar.onclick = barAlert;
    bar.textContent = state.state;

    // add bar to the chart 
    chart.appendChild(bar);
  };
};

function addYearSelectOptions(start, end) {
  let yearSelect = document.querySelector('#yearSelect');
  yearSelect.onchange = render;
  let year = end 
  // add an option for each year in the range of years available
  while (year >= start) {
    let option = document.createElement('option');
    option.value = year;
    option.textContent = year;
    yearSelect.appendChild(option);
    year--;
  };
};

function removeChildren(element) {
  while (element.lastChild) {
    element.removeChild(element.lastChild);
  };
};

function updateChartTitleYears(selected_year) {
  for (let title of document.querySelectorAll('.Chart__title')) {
    title.textContent = title.textContent.slice(0, -4) + selected_year;
  };
};

function barAlert(event) {
  let element = event.srcElement;
  let state = element.textContent.trim();
  let year = element.getAttribute("year");
  let data = element.getAttribute("data-value");
  let message = state
    + ' emitted '
    + data
    + ' million metric tons of CO2 in '
    + year;
  alert(message);
};


// initialize one time then render
initialize();
render();
