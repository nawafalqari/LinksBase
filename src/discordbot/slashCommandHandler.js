function createCommand(client) {
    const data = {
        name: 'user',
        description: `Get user's profile and QR Code.`
    }
    const commands = []

    commands.push(data)

    client.application.commands.set(commands)
}

module.exports = { createCommand }