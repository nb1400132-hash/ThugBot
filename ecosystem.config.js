module.exports = {
  apps: [{
    name: 'thugbot',
    script: 'main.py',
    interpreter: 'python3',
    autorestart: true,
    max_restarts: 10,
    watch: false,
    env: {
      PYTHONUNBUFFERED: '1'
    }
  }]
}
