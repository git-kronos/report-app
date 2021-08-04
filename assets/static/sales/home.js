console.log('hello world');

const reportBtn = document.getElementById('report-btn')
const img = document.getElementById('img')

console.log(reportBtn)
console.log(img)
if (img !== null){
    reportBtn.removeAttribute('hidden')
    console.log('hello')
}