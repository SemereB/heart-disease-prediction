document.addEventListener('DOMContentLoaded', function() {
        const form = document.getElementById('predictionForm');
        const historyToggle = document.getElementById('historyToggle');
        const historyPanel = document.getElementById('historyPanel');
        const clearHistoryBtn = document.getElementById('clearHistory');
        const historyItems = document.getElementById('historyItems');

        // New elements for loader and modal
        const loaderOverlay = document.getElementById('loaderOverlay');
        const resultModal = document.getElementById('resultModal');
        const closeModalButton = document.getElementById('closeModalButton');
        const modalResultContent = document.getElementById('modalResultContent');

        // Toggle history panel
        historyToggle.addEventListener('click', () => {
            historyPanel.classList.toggle('active');
        });

        // Load prediction history from localStorage
        loadHistory();

        form.addEventListener('submit', async function(e) {
            e.preventDefault();

            const formData = new FormData(form);
            const patientData = {
                Age: parseInt(formData.get('Age')),
                Sex: formData.get('Sex'),
                ChestPainType: formData.get('ChestPainType'),
                RestingBP: parseInt(formData.get('RestingBP')),
                Cholesterol: parseInt(formData.get('Cholesterol')),
                FastingBS: parseInt(formData.get('FastingBS')), // Already a string "0" or "1", parseInt is fine
                RestingECG: formData.get('RestingECG'),
                MaxHR: parseInt(formData.get('MaxHR')),
                ExerciseAngina: formData.get('ExerciseAngina'),
                Oldpeak: parseFloat(formData.get('Oldpeak')),
                ST_Slope: formData.get('ST_Slope')
            };

            // Show loader
            loaderOverlay.classList.add('active');

            //https://InfoScience.pythonanywhere.com/predict
            //http://localhost:8000/predict

            try {
                const response = await fetch("/predict", {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(patientData)
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({ detail: 'Network response was not ok and error details are unavailable.' }));
                    throw new Error(errorData.detail || HTTP error! status: ${response.status});
                }

                const result = await response.json();

                displayResult(result, patientData);
                saveToHistory(result, patientData);
                loadHistory();

            } catch (error) {
                console.error('Error:', error);
                modalResultContent.innerHTML = 
                    <div class="result-risk error-message">
                        <h3>Assessment Error</h3>
                        <p>An error occurred while processing your request.</p>
                        <p><strong>Details:</strong> ${error.message}</p>
                    </div>
                ;
                resultModal.classList.add('active');
            } finally {
                // Hide loader
                loaderOverlay.classList.remove('active');
            }
        });

        // Clear history
        clearHistoryBtn.addEventListener('click', () => {
            localStorage.removeItem('heartDiseasePredictions');
            historyItems.innerHTML = '<p>No prediction history found.</p>';
        });

        // Display prediction result in modal
        function displayResult(result, inputData) {
            const riskClass = result.prediction === 1 ? 'high-risk' : 'low-risk';
            const riskText = result.prediction === 1 ? 'High Risk' : 'Low Risk';
            const probabilityPercent = (result.probability * 100).toFixed(1);
            modalResultContent.innerHTML = 
                <div class="result-risk ${riskClass}">
                    <h3>${riskText}</h3>
                    <p>Confidence: ${probabilityPercent}%</p>
                </div>
                <div class="result-explanation">
                    <p>${result.explanation || 'Detailed explanation not available for this assessment.'}</p>
                </div>
                <div class="result-details">
                    <h4>Important Note:</h4>
                    <p>This assessment is based on a predictive model and is not a medical diagnosis. Please consult with a healthcare professional for any medical advice or concerns.</p>
                </div>
            ;
            resultModal.classList.add('active');
        }

        // Save prediction to history
        function saveToHistory(result, inputData) {
            let history = JSON.parse(localStorage.getItem('heartDiseasePredictions')) || [];
            history.unshift({
                input: inputData,
                result: result,
                timestamp: new Date().toLocaleString()
            });
            if (history.length > 20) {
                history = history.slice(0, 20);
            }
            localStorage.setItem('heartDiseasePredictions', JSON.stringify(history));
        }

        // Load prediction history
        function loadHistory() {
            const history = JSON.parse(localStorage.getItem('heartDiseasePredictions')) || [];

            if (history.length === 0) {
                historyItems.innerHTML = '<p>No prediction history found.</p>';
                return;
            }

            historyItems.innerHTML = '';

            history.forEach((item, index) => {
                const riskClass = item.result.prediction === 1 ? 'high-risk' : 'low-risk';
                const riskText = item.result.prediction === 1 ? 'High Risk' : 'Low Risk';
                const probabilityPercent = (item.result.probability * 100).toFixed(1);

                const historyItem = document.createElement('div');
                historyItem.className = 'history-item';
                historyItem.innerHTML = 
                    <div class="history-item-header">
                        <span>${item.timestamp}</span>
                      <span class="history-item-delete" data-index="${index}">Delete</span>
                    </div>
                    <div class="history-item-content">
                        <p>Age: ${item.input.Age}, Sex: ${item.input.Sex === 'M' ? 'Male' : 'Female'}</p>
                        <p>Chol: ${item.input.Cholesterol}, BP: ${item.input.RestingBP}, MaxHR: ${item.input.MaxHR}</p>
                    </div>
                    <div class="history-item-risk ${riskClass}">
                        ${riskText} (${probabilityPercent}%)
                    </div>
                ;
                historyItems.appendChild(historyItem);
            });

            document.querySelectorAll('.history-item-delete').forEach(button => {
                button.addEventListener('click', function(e) {
                    e.stopPropagation();
                    const index = parseInt(this.getAttribute('data-index'));
                    deleteHistoryItem(index);
                });
            });
        }

        // Delete a history item
        function deleteHistoryItem(index) {
            let history = JSON.parse(localStorage.getItem('heartDiseasePredictions')) || [];
            if (index >= 0 && index < history.length) {
                history.splice(index, 1);
                localStorage.setItem('heartDiseasePredictions', JSON.stringify(history));
                loadHistory();
            }
        }

        // Modal close functionality
        closeModalButton.addEventListener('click', () => {
            resultModal.classList.remove('active');
        });resultModal.addEventListener('click', (event) => {
            if (event.target === resultModal) { // Click on overlay
                resultModal.classList.remove('active');
            }
        });

        window.addEventListener('keydown', (event) => {
            if (event.key === 'Escape' && resultModal.classList.contains('active')) {
                resultModal.classList.remove('active');
            }
        });
    });