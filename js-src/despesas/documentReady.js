const documentReady = () =>
  new Promise((resolve) => {
    window.addEventListener('DOMContentLoaded', (event) => {
      setTimeout(() => {
        console.log('resolve');
        resolve();
      }, 100);
    });
  });

module.exports = documentReady;
