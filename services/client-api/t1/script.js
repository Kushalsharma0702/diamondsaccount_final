document.addEventListener('DOMContentLoaded', function() {
    const formSteps = document.querySelectorAll('.form-step');
    const progressBar = document.querySelector('.progress-bar');
    const stepLabels = document.querySelectorAll('.step-label');
    let currentStep = 0; // Start at the first step (index 0)

    // Function to update form visibility and progress bar
    function updateFormVisibility() {
        formSteps.forEach((step, index) => {
            if (index === currentStep) {
                step.style.display = 'block'; // Make it visible for animation
                setTimeout(() => {
                    step.classList.add('active'); // Trigger slide-in animation
                }, 10); // Small delay to ensure display:block applies before animation
            } else {
                step.classList.remove('active'); // Ensure it slides out if active
                // After animation, hide it
                step.addEventListener('transitionend', function handler() {
                    if (!step.classList.contains('active')) {
                        step.style.display = 'none';
                        step.removeEventListener('transitionend', handler);
                    }
                });
            }
        });

        // Update progress bar
        const progressPercentage = (currentStep / (formSteps.length - 1)) * 100;
        progressBar.style.width = progressPercentage + '%';
        progressBar.setAttribute('aria-valuenow', progressPercentage);

        // Update step labels
        stepLabels.forEach((label, index) => {
            if (index === currentStep) {
                label.classList.add('active-label');
            } else {
                label.classList.remove('active-label');
            }
        });

        // Scroll to the top of the form for better UX
        document.querySelector('.container').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // Initialize the form to show only the first step
    updateFormVisibility();

    // Navigation Buttons
    document.querySelectorAll('.next-step-btn').forEach(button => {
        button.addEventListener('click', () => {
            if (currentStep < formSteps.length - 1) {
                formSteps[currentStep].classList.add('leaving'); // Add leaving class for exit animation
                currentStep++;
                updateFormVisibility();
                setTimeout(() => {
                    formSteps[currentStep - 1].classList.remove('leaving'); // Remove leaving class after transition
                }, 500); // Match CSS transition duration
            }
        });
    });

    document.querySelectorAll('.prev-step-btn').forEach(button => {
        button.addEventListener('click', () => {
            if (currentStep > 0) {
                formSteps[currentStep].classList.add('leaving-reverse'); // Add leaving class for exit animation (reverse)
                currentStep--;
                updateFormVisibility();
                setTimeout(() => {
                    formSteps[currentStep + 1].classList.remove('leaving-reverse'); // Remove leaving class after transition
                }, 500); // Match CSS transition duration
            }
        });
    });

    // Helper function to toggle section visibility
    function toggleSection(radioGroupName, sectionId) {
        const radios = document.querySelectorAll(`input[name="${radioGroupName}"]`);
        const section = document.getElementById(sectionId);

        radios.forEach(radio => {
            radio.addEventListener('change', function() {
                if (this.value === 'yes' && this.checked) {
                    section.style.display = 'block';
                    setTimeout(() => section.style.opacity = '1', 10); // Smooth fade in
                } else {
                    section.style.opacity = '0';
                    setTimeout(() => section.style.display = 'none', 300); // Fade out then hide
                }
            });
        });

        // Initial check on page load
        const checkedRadio = document.querySelector(`input[name="${radioGroupName}"]:checked`);
        if (checkedRadio && checkedRadio.value === 'yes') {
            section.style.display = 'block';
            section.style.opacity = '1';
        } else {
            section.style.display = 'none';
            section.style.opacity = '0';
        }
    }

    // Conditional logic for Questionnaire sections
    toggleSection('foreignProperty', 'foreignPropertyDetails');
    toggleSection('medicalExpenses', 'medicalExpensesDetails');
    toggleSection('charitableDonations', 'charitableDonationsDetails');
    toggleSection('movingExpenses', 'movingExpenseDetails');
    toggleSection('selfEmployed', 'selfEmployedDetails');
    toggleSection('soldPropertyLong', 'soldPropertyLongDetails');
    toggleSection('soldPropertyShort', 'soldPropertyShortDetails');
    toggleSection('wfhExpense', 'wfhExpenseDetails');
    toggleSection('unionMember', 'unionDuesDetails');
    toggleSection('daycareExpenses', 'daycareExpensesDetails');
    toggleSection('firstTimeFiler', 'firstTimeFilerDetails');
    toggleSection('otherIncome', 'otherIncomeDetails');
    toggleSection('professionalDues', 'professionalDuesDetails');
    toggleSection('childArtSportCredit', 'childArtSportCreditDetails');
    toggleSection('provinceFiler', 'provinceFilerDetails');

    // Marital Status - Spouse Details
    const maritalStatusSelect = document.getElementById('maritalStatus');
    const spouseDetailsSection = document.getElementById('spouseDetails');

    maritalStatusSelect.addEventListener('change', function() {
        if (this.value === 'married' || this.value === 'common-law') {
            spouseDetailsSection.style.display = 'block';
            setTimeout(() => spouseDetailsSection.style.opacity = '1', 10);
        } else {
            spouseDetailsSection.style.opacity = '0';
            setTimeout(() => spouseDetailsSection.style.display = 'none', 300);
        }
    });
    // Initial check for marital status
    if (maritalStatusSelect.value === 'married' || maritalStatusSelect.value === 'common-law') {
        spouseDetailsSection.style.display = 'block';
        spouseDetailsSection.style.opacity = '1';
    }


    // Self-Employment Type - Conditional Sections
    const businessTypeRadios = document.querySelectorAll('input[name="businessType"]');
    const uberSkipDoordashSection = document.getElementById('uberSkipDoordashSection');
    const generalBusinessSection = document.getElementById('generalBusinessSection');
    const rentalIncomeSection = document.getElementById('rentalIncomeSection');

    function toggleBusinessTypeSections() {
        // Fade out all first, then show the selected one
        [uberSkipDoordashSection, generalBusinessSection, rentalIncomeSection].forEach(sec => {
            sec.style.opacity = '0';
            setTimeout(() => sec.style.display = 'none', 300);
        });

        businessTypeRadios.forEach(radio => {
            if (radio.checked) {
                let targetSection;
                if (radio.value === 'uber') {
                    targetSection = uberSkipDoordashSection;
                } else if (radio.value === 'general') {
                    targetSection = generalBusinessSection;
                } else if (radio.value === 'rental') {
                    targetSection = rentalIncomeSection;
                }

                if (targetSection) {
                    setTimeout(() => { // Small delay after hiding others to prevent flicker
                        targetSection.style.display = 'block';
                        setTimeout(() => targetSection.style.opacity = '1', 10);
                    }, 300);
                }
            }
        });
    }

    businessTypeRadios.forEach(radio => {
        radio.addEventListener('change', toggleBusinessTypeSections);
    });

    toggleBusinessTypeSections(); // Call on load to set initial state


    // Dynamic row additions for tables
    function addTableRow(buttonId, tableBodyId, rowHTML) {
        document.getElementById(buttonId).addEventListener('click', function() {
            const tableBody = document.querySelector(`#${tableBodyId} tbody`);
            const newRow = tableBody.insertRow();
            newRow.innerHTML = rowHTML;
            // Re-index 'No.' column if present (e.g., for foreign property, child art/sport)
            if (tableBodyId.includes('foreignPropertyDetails') || tableBodyId.includes('childArtSportCreditDetails')) {
                const rows = tableBody.rows;
                for (let i = 0; i < rows.length; i++) {
                    const firstCell = rows[i].cells[0];
                    if (firstCell && firstCell.tagName === 'TD') { // Ensure it's a data cell
                        firstCell.textContent = i + 1;
                    }
                }
            }
        });
    }

    addTableRow('addForeignPropertyRow', 'foreignPropertyDetails', `
        <td></td>
        <td><input type="text" class="form-control form-control-sm"></td>
        <td><input type="number" class="form-control form-control-sm"></td>
        <td><input type="number" class="form-control form-control-sm"></td>
        <td><input type="number" class="form-control form-control-sm"></td>
        <td><input type="number" class="form-control form-control-sm"></td>
        <td><input type="text" class="form-control form-control-sm"></td>
    `);

    addTableRow('addMedicalExpenseRow', 'medicalExpensesDetails', `
        <td><input type="date" class="form-control form-control-sm"></td>
        <td><input type="text" class="form-control form-control-sm"></td>
        <td><input type="text" class="form-control form-control-sm"></td>
        <td><input type="text" class="form-control form-control-sm"></td>
        <td><input type="number" class="form-control form-control-sm"></td>
        <td><input type="number" class="form-control form-control-sm"></td>
    `);

    addTableRow('addCharitableDonationRow', 'charitableDonationsDetails', `
        <td><input type="text" class="form-control form-control-sm"></td>
        <td><input type="number" class="form-control form-control-sm"></td>
    `);

    addTableRow('addUnionDuesRow', 'unionDuesDetails', `
        <td><input type="text" class="form-control form-control-sm"></td>
        <td><input type="number" class="form-control form-control-sm"></td>
    `);

    addTableRow('addDaycareExpenseRow', 'daycareExpensesDetails', `
        <td><input type="text" class="form-control form-control-sm"></td>
        <td><input type="text" class="form-control form-control-sm"></td>
        <td><input type="number" class="form-control form-control-sm"></td>
        <td><input type="number" class="form-control form-control-sm"></td>
    `);

    addTableRow('addProfessionalDuesRow', 'professionalDuesDetails', `
        <td><input type="text" class="form-control form-control-sm"></td>
        <td><input type="text" class="form-control form-control-sm"></td>
        <td><input type="number" class="form-control form-control-sm"></td>
    `);

    addTableRow('addChildArtSportRow', 'childArtSportCreditDetails', `
        <td></td>
        <td><input type="text" class="form-control form-control-sm"></td>
        <td><input type="text" class="form-control form-control-sm"></td>
        <td><input type="number" class="form-control form-control-sm"></td>
    `);

    addTableRow('addProvinceFilerRow', 'provinceFilerDetails', `
        <td><input type="text" class="form-control form-control-sm" placeholder="Rent or Property Tax"></td>
        <td><input type="text" class="form-control form-control-sm"></td>
        <td><input type="text" class="form-control form-control-sm"></td>
        <td><input type="number" class="form-control form-control-sm"></td>
        <td><input type="number" class="form-control form-control-sm"></td>
    `);

    // Dynamic child addition in Personal Information
    const childrenContainer = document.getElementById('childrenContainer');
    const addChildBtn = document.getElementById('addChildBtn');
    let childCount = 0; // Start at 0, first child will be "Child 1"

    function addChildRow() {
        childCount++;
        const childDiv = document.createElement('div');
        childDiv.classList.add('child-entry', 'mt-3', 'p-3', 'bg-white', 'rounded-3', 'shadow-sm');
        childDiv.innerHTML = `
            <h6 class="mb-3">Child ${childCount} Details</h6>
            <div class="mb-3">
                <label class="form-label fw-bold">Name as per SIN Document (Child ${childCount})</label>
                <div class="row g-3">
                    <div class="col-md-4">
                        <input type="text" class="form-control" placeholder="First Name (Child ${childCount})">
                    </div>
                    <div class="col-md-4">
                        <input type="text" class="form-control" placeholder="Middle Name (Child ${childCount})">
                    </div>
                    <div class="col-md-4">
                        <input type="text" class="form-control" placeholder="Last Name (Child ${childCount})">
                    </div>
                </div>
            </div>
            <div class="row g-3 mb-3">
                <div class="col-md-6">
                    <label class="form-label">SIN (Child ${childCount})</label>
                    <input type="text" class="form-control" placeholder="Child ${childCount} SIN">
                </div>
                <div class="col-md-6">
                    <label class="form-label">Date of Birth (DD/MM/YYYY) (Child ${childCount})</label>
                    <input type="date" class="form-control">
                </div>
            </div>
            <button type="button" class="btn btn-outline-danger btn-sm remove-child-btn">Remove Child</button>
        `;
        childrenContainer.appendChild(childDiv);

        // Add event listener to the new remove button
        childDiv.querySelector('.remove-child-btn').addEventListener('click', function() {
            childrenContainer.removeChild(childDiv);
            reindexChildren(); // Re-index after removal
        });
    }

    function reindexChildren() {
        const childEntries = childrenContainer.querySelectorAll('.child-entry');
        childCount = 0; // Reset count
        childEntries.forEach((entry, index) => {
            childCount = index + 1;
            entry.querySelector('h6').textContent = `Child ${childCount} Details`;
            entry.querySelectorAll('input').forEach(input => {
                const placeholder = input.placeholder;
                if (placeholder && placeholder.includes('Child ')) {
                    input.placeholder = placeholder.replace(/Child \d+/, `Child ${childCount}`);
                }
                // Update label for attribute if present
                const inputId = input.id;
                if (inputId) {
                    const label = entry.querySelector(`label[for="${inputId}"]`);
                    if (label && label.textContent.includes('Child ')) {
                        label.textContent = label.textContent.replace(/Child \d+/, `Child ${childCount}`);
                    }
                }
            });
        });
    }

    addChildBtn.addEventListener('click', addChildRow);

    // Add initial child row on load
    addChildRow();
});