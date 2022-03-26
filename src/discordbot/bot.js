require('dotenv').config()

const { Client, Intents, MessageEmbed, Constants } = require('discord.js')
const client = new Client({ intents: new Intents(32767) })

const fs = require('fs')

const api = require('./api.js')
const links_scanner = require('./links_scanner.js')

let linksbase_guild_id = '930807810659319868'

client.on('ready', async () => {
    console.log(`Logged in as ${client.user.tag}`)

    client.user.setActivity('LinksBase :)', {type: 'PLAYING'})
    
    // const commands = await client.application.commands
    const commands = await client.guilds.cache.get(linksbase_guild_id).commands

    // const command = await client.guilds.cache.get(linksbase_guild_id)?.commands.fetch('956243342402912326');
    // await command.delete();

    // console.log(
    //     await client.api.applications(client.user.id).commands.post({
    //         data: {
    //           name: 'hello',
    //           description: 'Replies with pong!',
    //         },
    //       })
    // )
    // 956243342402912326
    // 952074977430085662

    commands.create({
        name: 'user',
        description: `Get User's profile and QR Code.`,
        options: [
            {
                name: 'username',
                description: `Target's Username`,
                required: true,
                type: Constants.ApplicationCommandOptionTypes.STRING
            }
        ]
    })
    console.log('CREATED /user')
})

client.on('messageCreate', async (message) => {
    if(message.author.bot) return;

    message.channel.send(`${message.content.search(/((([A-Za-z]{3,9}:(?:\/\/)?)(?:[\-;:&=\+\$,\w]+@)?[A-Za-z0-9\.\-]+|(?:www\.|[\-;:&=\+\$,\w]+@)[A-Za-z0-9\.\-]+)((?:\/[\+~%\/\.\w\-_]*)?\??(?:[\-\+=&;%@\.\w_]*)#?(?:[\.\!\/\\\w]*))?)/)}`)

    if(message.content.startsWith('!user')) {
        let username = message.content.split(' ')
        
        if(username.length == 1) return message.reply(`Usage: !user {username}`)
        username = username[username.length - 1]
        
        data_res = await api.get(username)
        qrcode_res = await api.get_qrcode(username)

        if(data_res['_error'] == true) {
            return message.reply('Error: User Does Not Exist!')
        }

        let embed = new MessageEmbed()
        .setTitle(`LinksBase | ${data_res['username']}`)
        .setURL(data_res['data']['url'])
        .setDescription(data_res['data']['description'])
        .setColor('0057c0')
        .setThumbnail(data_res['avatar'])
        .setImage(data_res['qr_code'])
        .setTimestamp()
        .setFooter({
            text: 'api.linksb.me',
            iconURL: client.user.avatarURL
        })

        return message.channel.send({embeds: [embed]})
    }
})

client.on('interactionCreate', async (interaction) => {
    if(!interaction.isCommand()) return

    if(interaction.commandName == 'user') {
        interaction.deferReply()

        let username = interaction.options.getString('username')
        
        data_res = await api.get(username)
        qrcode_res = await api.get_qrcode(username)

        if(data_res['_error'] == true) {
            return interaction.editReply('Error: User Does Not Exist!')
        }

        let embed = new MessageEmbed()
        .setTitle(`LinksBase | ${data_res['username']}`)
        .setURL(data_res['data']['url'])
        .setDescription(data_res['data']['description'])
        .setColor('0057c0')
        .setThumbnail(data_res['avatar'])
        .setImage(data_res['qr_code'])
        .setTimestamp()
        .setFooter({
            text: 'api.linksb.me',
            iconURL: client.user.avatarURL
        })

        return interaction.editReply({
            embeds: [embed]
        })
    }
})

client.login(process.env.BOT_TOKEN)