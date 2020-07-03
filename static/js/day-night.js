let loaded = () => {
    // Starting RBGA
    let start_day = [0, 200, 255, 1];
    let color = [0, 200, 255, 1];
    let day_target = [0, 70, 255, 1];
    let input = document.getElementById("project_minutes");
    let range = input.max - input.min;

    let updateStyling = (event) => {
        let value = event.target.value;
        if (value < range / 2) {
            let percent = 2 * value / range;
            color = [0, (200 - 130 * percent), 255, 1];
            event.target.parentNode.style.backgroundColor = "rgba(0, " + color[1] + ", 255, 1)";

            try {
                event.target.parentNode.classList.remove("night");
            } catch (e) {}
        }
        else {
            let percent = 2 * (value - range / 2) / range;
            color = [0, 70 - 27 * percent, 255 - 135 * percent, 1];
            event.target.parentNode.style.backgroundColor = "rgba(0, " + color[1] + ", " + color[2] + ", 1)";

            event.target.parentNode.classList.add("night");
        }

        let start = document.getElementById("project_minutes").getBoundingClientRect()
        let width = start.right - start.left;

        let x = width * value / range + 24;
        document.getElementById("project_minutes_tooltips").style.left = x + "px"
        document.getElementById("project_minutes_tooltips").style.opacity = 1;

        let unit = "minutes";
        if (value == 1) {
            unit = "minute";
        }
        else if (value == 181) {
            unit = "hours"
            value = "3+"
        }
        else if (value > 60) {
            unit = "hours";
            value = Math.round(value / 15) / 4;
        }

        if (value == 1 && unit == "hours") {
            unit = "hour"
        }

        document.getElementById("time_spent").innerText = value;
        document.getElementById("time_unit").innerText = unit;
    };
    input.addEventListener("input", updateStyling);

    input.addEventListener("change", (event) => {
        document.getElementById("project_minutes_tooltips").style.opacity = 0;
    });
};

if (document.readyState === "complete")
    loaded();
else
    document.addEventListener("DOMContentLoaded", loaded);
