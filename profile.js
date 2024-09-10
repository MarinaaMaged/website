function updateProfile() {
    const name = document.getElementById('nameInput').value;
    const weight = document.getElementById('weightInput').value;
    const age = document.getElementById('ageInput').value;
    const goals = document.getElementById('goalsInput').value;

    document.getElementById('nameDisplay').textContent = name || 'Name';
    document.getElementById('weightDisplay').textContent = weight ? weight + ' kg' : '... kg';
    document.getElementById('ageDisplay').textContent = age ? age + ' years' : '... years';
    document.getElementById('goalsDisplay').textContent = goals || '...';
}

document.getElementById('profilePicInput').addEventListener('change', function (event) {
    const reader = new FileReader();
    reader.onload = function () {
        document.getElementById('profilePic').src = reader.result;
    };
    reader.readAsDataURL(event.target.files[0]);
});
