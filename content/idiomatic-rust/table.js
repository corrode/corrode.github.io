// Formatting function for row details
function format(d) {
  // `d` is the original data object for the row
  return "<dl>" + "<dt></dt>" + "<dd>" + d.description + "</dd>" + "</dl>";
}

function capitalizeFirstLetter(string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}

function renderCategory(category) {
  let symbol =
    category === "article"
      ? "📝"
      : category === "video"
      ? "📺"
      : category === "guide"
      ? "📖"
      : category === "forum"
      ? "💬"
      : category === "talk"
      ? "🎤️"
      : category === "workshop"
      ? "🏋️"
      : category === "project"
      ? "⚙"
      : "📚";
  return symbol + " " + capitalizeFirstLetter(category);
}

// Wait for dom content to be loaded with jquery
$(document).ready(function () {
  const table = new DataTable("#data-table", {
    ajax: "/idiomatic-rust/data.json",
    // Add dropdown filters for columns
    initComplete: function () {
      this.api()
        .columns([1, 7, 9, 10])
        .every(function () {
          let column = this;

          // Create select element
          let select = document.createElement("select");
          select.add(new Option(""));

          // Add select element to the table header
          $(column.header()).append(select);

          // Apply listener for user change in value
          select.addEventListener("change", function () {
            var val = DataTable.util.escapeRegex(select.value);

            column.search(val ? "^" + val + "$" : "", true, false).draw();
          });

          // Add list of options
          column
            .cells("", column[0])
            .render("display")
            .sort()
            .unique()
            .each(function (d, j) {
              select.add(new Option(d));
            });
        });
    },
    paging: false,
    scrollCollapse: true,
    order: [[7, "asc"]],
    columns: [
      {
        className: "dt-control",
        orderable: false,
        data: null,
        defaultContent: "",
      },
      {
        data: "category",
        title: "Category",
        render: function (data) {
          return renderCategory(data);
        },
      },
      {
        data: "title",
        title: "Title",
        render: function (data, type, row) {
          return (
            '<a target="_blank" rel="noopener noreferrer" href="' +
            row.url +
            '">' +
            row.title +
            "</a>"
          );
        },
      },
      { data: "description", title: "Description", visible: false },
      {
        data: "tags",
        title: "Tags",
        // Format as `<code>` tags
        render: function (data) {
          return data
            .map((tag) => '<code style="margin:5px 0">' + tag + "</code>")
            .join(" ");
        },
        visible: true,
      },
      {
        data: "official",
        title: "Official",
        visible: false,
        render: function (data, type, row) {
          return data ? "✅" : "❌";
        },
      },
      { data: "year", title: "Year", visible: false },
      {
        data: "difficultyLevel",
        title: "Difficulty",
        // Render as emoji stars (beginner: 1, intermediate: 2, advanced: 3)
        render(data) {
          if (data === "beginner" || data === "all" || data === "varied") {
            return '<span class="difficultyLevel">➕</span>';
          } else if (data === "intermediate") {
            return '<span class="difficultyLevel">➕➕</span>';
          } else if (data === "advanced") {
            return '<span class="difficultyLevel">➕➕➕</span>';
          } else {
            return data;
          }
        },
      },
      {
        data: "duration",
        title: "Duration",
        visible: false,
      },
      {
        data: "interactivityLevel",
        title: "Interactivity",
        render(data) {
          if (data === "low") {
            return "⚙";
          } else if (data === "medium") {
            return "️⚙⚙";
          } else if (data === "high") {
            return "⚙⚙⚙";
          } else {
            return data;
          }
        },
      },
      {
        data: "free",
        title: "Free",
        visible: false,
        render: function (data, type, row) {
          return data ? "✅" : "❌";
        },
      },
    ],
  });

  // Object to keep track of active filters
  var activeFilters = {};

  // Define a custom filtering function
  $.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {
    // If no filters are active, show all rows
    if (Object.keys(activeFilters).length === 0) {
      return true;
    }

    // Get the tags for the current row (assuming they are in column 4)
    var tags = data[4];

    // All active filters must match
    return Object.keys(activeFilters).every(function (tag) {
      return tags.includes(tag);
    });
  });

  // Add event listener to code tags for toggling filter
  $(".dataTables_wrapper").on("click", "code", function () {
    var tag = $(this).text();

    // Toggle the tag in active filters
    if (activeFilters[tag]) {
      delete activeFilters[tag];
      $("code")
        .filter(function () {
          return $(this).text().includes(tag);
        })
        .removeClass("active");
    } else {
      activeFilters[tag] = true;
      $("code")
        .filter(function () {
          return $(this).text().includes(tag);
        })
        .addClass("active");
    }

    if (Object.keys(activeFilters).length > 0) {
      /* set display: block to the reset button */
      $(".reset-filter").css("display", "block");
    } else {
      /* set display: none to the reset button */
      $(".reset-filter").css("display", "none");
    }

    // Trigger a redraw to apply the new filter
    table.draw();
  });

  // Add event listener for opening and closing details
  table.on("click", "td.dt-control", function (e) {
    let tr = e.target.closest("tr");
    let row = table.row(tr);

    if (row.child.isShown()) {
      // This row is already open - close it
      row.child.hide();
    } else {
      // Open this row
      row.child(format(row.data())).show();
    }
  });

  // Reset all filters when clicking the reset button
  $(".reset-filter").on("click", function () {
    activeFilters = {};
    $("code").removeClass("active");
    $(".reset-filter").css("display", "none");
    table.draw();
  });

  document.querySelectorAll("a.toggle-vis").forEach((el) => {
    el.addEventListener("click", function (e) {
      e.preventDefault();

      let columnIdx = e.target.getAttribute("data-column");
      let column = table.column(columnIdx);

      // Toggle the visibility
      column.visible(!column.visible());

      // Toggle the active class for the a.toggle-vis element
      e.target.classList.toggle("active");
    });
  });
});
