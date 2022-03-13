require('dotenv').config()

const { Client, Intents, Collection } = require('discord.js')
const client = new Client({ intents: new Intents(32767) })

const fs = require('fs')



client.on('ready', () => {
    console.log(`Logged in as ${client.user.tag}`)
    // const { createCommand } = require('./slashCommandHandler.js')
    // createCommand(client)
})

client.on('interactionCreate', i => {
    if(!i.isCommand() || i.user.bot) return;

    if (i.commandName === 'hello') {
        i.reply('Pong!')
    }

    if (i.commandName === 'user') {
        i.reply('Hello world!')
    }
})

client.login(process.env.BOT_TOKEN)