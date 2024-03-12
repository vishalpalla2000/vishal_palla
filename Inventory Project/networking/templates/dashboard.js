$(document).ready(function () {
        function updateCounts(selectedYear) {
            const today = new Date();
            const upsSquareCard = document.getElementById("upsSquareCard");
            const batterySquareCard = document.getElementById("batterySquareCard");
            let upsCount = 0;
            let batteryCount = 0;

            // Iterate over table rows and calculate counts
            const tableRows = document.querySelectorAll("table tbody tr");
            tableRows.forEach((row) => {
                const upsInstalledDate = new Date(row.querySelector("td:nth-child(8)").textContent);
                const batteryInstalledDate = new Date(row.querySelector("td:nth-child(7)").textContent);

                // Calculate the expiration date for UPS and Battery
                const upsExpirationDate = new Date(upsInstalledDate);
                const batteryExpirationDate = new Date(batteryInstalledDate);

                upsExpirationDate.setFullYear(upsExpirationDate.getFullYear() + 5); // UPS expires in 5 years
                batteryExpirationDate.setFullYear(batteryExpirationDate.getFullYear() + 2); // Battery expires in 2 years

                // Calculate the time difference in days
                const upsDays = Math.floor((upsExpirationDate - today) / (1000 * 60 * 60 * 24));
                const batteryDays = Math.floor((batteryExpirationDate - today) / (1000 * 60 * 60 * 24));

                // Check if the expiration dates are within the selected number of days
                if (upsDays <= selectedYear * 365) {
                    upsCount++;
                }

                if (batteryDays <= selectedYear * 365) {
                    batteryCount++;
                }
            });

            upsSquareCard.querySelector("p").textContent = upsCount.toString();
            batterySquareCard.querySelector("p").textContent = batteryCount.toString();
        }

        // Event listener for the select box change
        const expiryYearSelect = document.getElementById("expiryYearSelect");
        expiryYearSelect.addEventListener("change", (event) => {
            const selectedYear = parseInt(event.target.value);
            updateCounts(selectedYear);
        });

        // Initial update based on the default selected year
        const initialSelectedYear = parseInt(expiryYearSelect.value);
        updateCounts(initialSelectedYear);
    // Edit button click event listener for the header
    $(".edit-button-header").on("click", function () {
        // Show the edit popup
        $("#editPopup").modal("show");

        // Clear the previous values from the form
        $("#ipAddressSelect").val(""); // Reset IP Address select
        $("#building").val("");
        $("#lanRoom").val("");

        // Populate the IP addresses from the SNMP table (Replace with your logic)
        // Example:
        // Fetch the IP addresses via an API or Django context data
        // and populate them in the select field

        // Fetch IP addresses dynamically and populate the select field here

        // When an IP Address is selected from the dropdown, populate the form
        $("#ipAddressSelect").on("change", function () {
            var selectedIP = $(this).val();
            // Fetch data associated with the selected IP from the manual table and populate the form fields
            // Example: Fetch data via AJAX
            // Update the 'building' and 'lanRoom' fields based on the selected IP
        });

        // Handle form submission for editing data
        $("#saveChanges").on("click", function () {
            // Get the values from the form
            var selectedIP = $("#ipAddressSelect").val();
            var building = $("#building").val();
            var lanRoom = $("#lanRoom").val();

            // Update the data in the manual table (Replace with your logic)
            // Example: Send data via AJAX to update the manual table

            // Close the edit popup
            $("#editPopup").modal("hide");
        });
    });
});
