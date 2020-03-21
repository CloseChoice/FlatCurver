/* eslint-disable no-undef */
/****** embed.api.js *******/

/**
 * javascript client that interacts with the embedding api
 *
 * KF.embed.klip(
 *
 */
export default function() {
    window.KF = window.KF || {}
    KF.embed = KF.embed || {}
    KF.embed = (function() {
        var imgAsset = 'https://embed.klipfolio.com/images/embed/assets.png'
        var spinnerAsset = 'https://embed.klipfolio.com/images/embed/spinner.gif'
        var klipUrl = 'https://embed.klipfolio.com/imaging/embed_klip/'
        var lastUpdatedUrl = 'https://embed.klipfolio.com/imaging/embed_last_updated/'

        var productNameText = 'Klipfolio'
        var actionText = 'Create your own dashboards'
        var actionLink =
            'http://www.klipfolio.com/?utm_source=klips&utm_medium=referral&utm_campaign=embedded_klips'

        var lightColor = '#666666'
        var darkColor = '#cccccc'

        var lightBgColor = '#fefefe'
        var darkBgColor = '#2a2a2a'

        var roundStyle = {
            borderRadius: '5px',
            MozBorderRadius: '5px',
            WebkitBorderRadius: '5px',
        }

        // DOM Manipulation Helper Methods
        // ---------------------------------------------

        function createNode(name) {
            return document.createElement(name)
        }

        function getNode(selector, type) {
            switch (type) {
                case 'id':
                    return document.getElementById(selector)
                case 'tagName':
                    return document.getElementsByTagName(selector)[0]
                default:
                    return null
            }
        }

        function appendChild(parent, child) {
            parent.appendChild(child)
        }

        function insertBefore(parent, newChild, existingChild) {
            parent.insertBefore(newChild, existingChild)
        }

        function removeChild(parent, child) {
            parent.removeChild(child)
        }

        function setAttributes(node, attrs) {
            var a
            for (a in attrs) {
                node.setAttribute(a, attrs[a])
            }
        }

        function addClass(node, className) {
            node.className += (node.className != '' ? ' ' : '') + className
        }

        function setStyles(node, styles) {
            var s
            for (s in styles) {
                node.style[s] = styles[s]
            }
        }

        function getStyle(node, style) {
            return node.style[style]
        }

        function setHtml(node, text) {
            node.innerHTML = text
        }

        function setText(node, text) {
            var i
            var children = node.childNodes
            for (i = 0; i < children.length; i++) node.removeChild(children[i])
            node.appendChild(document.createTextNode(text))
        }

        function getWidth(node) {
            return node.offsetWidth
        }

        function getHeight(node) {
            return node.offsetHeight
        }

        function getTop(node) {
            return node.offsetTop
        }

        function addEvent(node, evtName, fn) {
            if (node.addEventListener) {
                node.addEventListener(evtName, fn)
            } else {
                node.attachEvent('on' + evtName, fn)
            }
        }

        // ---------------------------------------------

        /**
         *
         * @param config = {
         * 	    url: "",
         * 	    profile: "",
         * 	    container: "",
         *      settings: {
         *          borderColor: "",
         *          borderStyle: "",
         *          theme: "",
         *          width: ""
         *      },
         *      title: "",
         *      description: "",
         *      productName: "",
         *      actionLink: "",
         *      actionText: "",
         *      isPreview: true
         * }
         */
        function embedKlip(config) {
            var settings = config.settings

            var root = createNode('div')
            setAttributes(root, { id: 'kf-embed-' + config.profile })
            addClass(root, 'kf-embed-klip')
            setStyles(root, {
                position: 'relative',
                fontFamily: 'Arial, Helvetica, sans-serif',
                fontSize: '11px',
                cursor: 'pointer',
            })

            // eslint-disable-next-line
            var mainTitle = createNode('div')
            addClass(mainTitle, 'kf-embed-mainTitle')
            setStyles(mainTitle, {
                marginBottom: '9px',
                color: settings.theme == 'dark' ? darkColor : lightColor,
                fontSize: '16px',
                lineHeight: '1.3em',
                fontWeight: 'bold',
            })
            setText(mainTitle, config.title)
            appendChild(root, mainTitle)

            // eslint-disable-next-line
            var spinner = createNode('div')
            addClass(spinner, 'kf-embed-spinner')
            setAttributes(spinner, { id: 'kf-embed-spinner-' + config.profile })
            setStyles(spinner, {
                height: '16px',
                width: '16px',
                backgroundImage: 'url(' + spinnerAsset + ')',
                backgroundRepeat: 'no-repeat',
            })

            // eslint-disable-next-line
            var info = createNode('div')
            addClass(info, 'kf-embed-info')

            // eslint-disable-next-line
            var title = createNode('div')
            addClass(title, 'kf-embed-title')

            // eslint-disable-next-line
            var description = createNode('div')
            addClass(description, 'kf-embed-description')

            // eslint-disable-next-line
            var lastUpdated = createNode('div')
            setAttributes(lastUpdated, { id: 'kf-embed-lastUpdated-' + config.profile })
            addClass(lastUpdated, 'kf-embed-lastUpdated')

            // eslint-disable-next-line
            var tweetButton = createNode('button')
            addClass(tweetButton, 'kf-embed-tweet')
            setHtml(tweetButton, 'Tweet')

            // eslint-disable-next-line
            var createLink = createNode('a')
            setAttributes(createLink, {
                href: config.actionLink ? config.actionLink : actionLink,
                target: '_blank',
            })
            addClass(createLink, 'kf-embed-create')
            setHtml(createLink, config.actionText ? config.actionText : actionText)

            // eslint-disable-next-line
            var foot = createNode('div')
            addClass(foot, 'kf-embed-footer')
            setStyles(foot, {
                position: 'relative',
                marginTop: '5px',
            })

            // eslint-disable-next-line
            var arrowBgPosition = settings.theme == 'dark' ? '-14px -36px' : '0 -36px'
            // eslint-disable-next-line
            var arrow = createNode('div')
            setStyles(arrow, {
                position: 'absolute',
                styleFloat: 'left', // for IE
                cssFloat: 'left',
                top: '7px',
                height: '7px',
                width: '14px',
                backgroundImage: 'url(' + imgAsset + ')',
                backgroundPosition: arrowBgPosition,
                backgroundRepeat: 'no-repeat',
                cursor: !config.isPreview ? 'pointer' : 'default',
            })
            appendChild(foot, arrow)

            // eslint-disable-next-line
            var productName = createNode('a')
            setAttributes(productName, {
                href: config.actionLink ? config.actionLink : actionLink,
                target: '_blank',
            })
            addClass(productName, 'kf-embed-productName')
            setStyles(productName, {
                styleFloat: 'right', // for IE
                cssFloat: 'right',
                color: '#898989',
                lineHeight: '16px',
                fontSize: '10px',
            })
            setHtml(productName, config.productName ? config.productName : productNameText)
            appendChild(foot, productName)

            // eslint-disable-next-line
            var reportText = createNode('div')
            setStyles(reportText, {
                styleFloat: 'right', // for IE
                cssFloat: 'right',
                marginRight: '3px',
                color: '#898989',
                lineHeight: '16px',
                fontSize: '10px',
            })
            setHtml(reportText, 'Powered by')
            appendChild(foot, reportText)

            // insert into page
            // eslint-disable-next-line
            var c = getNode(
                config.container ? config.container : 'kf-embed-container-' + config.profile,
                'id'
            )
            setStyles(c, { display: 'inline-block' })
            appendChild(c, root)

            // insert embed image
            var url // eslint-disable-line
            if (config.url) {
                url = config.url
            } else if (config.profile) {
                url = klipUrl + config.profile
            }

            // eslint-disable-next-line
            var img = createNode('img')
            setAttributes(img, { src: url })
            setStyles(img, { display: 'none' })
            appendChild(root, img)

            appendChild(root, spinner)
            appendChild(root, info)
            appendChild(root, foot)

            // apply settings
            // ------------------
            setStyles(root, {
                padding: '10px 10px 5px',
                overflow: 'hidden',
            })

            // eslint-disable-next-line
            //  var extraWidth = (/msie/i.test(navigator.userAgent) && !/opera/i.test(navigator.userAgent) ?
            //         ? 20 /* root padding */ + (settings.borderStyle ? 2 : 0) /* root border */
            //         : 0

            var extraWidth = 20

            if (settings.width) setStyles(root, { width: settings.width + extraWidth + 'px' })

            setStyles(root, {
                backgroundColor: settings.theme == 'dark' ? darkBgColor : lightBgColor,
            })

            if (settings.borderStyle) {
                var color = settings.borderColor // eslint-disable-line
                setStyles(root, { border: '1px solid ' + color })

                if (settings.borderStyle == 'round') setStyles(root, roundStyle)
            }

            // configure info panel
            // --------------------
            setStyles(info, {
                position: 'absolute',
                padding: '5px',
                backgroundColor: '#444444',
                border: '1px solid #000000',
                display: 'none',
                cursor: 'default',
                lineHeight: '20px',
            })

            if (settings.borderStyle == 'round') setStyles(info, roundStyle)

            setStyles(title, {
                marginBottom: '5px',
                color: '#ffffff',
                fontSize: '14px',
                fontWeight: 'bold',
            })
            setText(title, config.title)
            appendChild(info, title)

            if (config.description) {
                setStyles(description, {
                    marginBottom: '5px',
                    color: '#ffffff',
                    fontSize: '12px',
                })
                setText(description, config.description)
                appendChild(info, description)
            }

            setStyles(lastUpdated, {
                marginBottom: '5px',
                color: '#999999',
                fontSize: '11px',
            })
            setHtml(lastUpdated, 'Last updated:')
            appendChild(info, lastUpdated)

            //        setStyles(tweetButton, {
            //            marginBottom:"5px",
            //            cursor:"pointer",
            //            display:"block"
            //        });
            //        appendChild(info, tweetButton);

            setStyles(createLink, {
                color: '#49aeff',
                fontSize: '14px',
                fontWeight: 'bold',
                textDecoration: 'none',
            })
            appendChild(info, createLink)

            // add event listeners to embeds
            // -----------------------------

            // show/hide info panel
            addEvent(root, 'click', function() {
                var isVisible = getStyle(info, 'display') != 'none'
                var infoPaddingBorder

                if (isVisible) {
                    setStyles(info, { display: 'none' })
                } else {
                    // add in the script to get the last updated date
                    // ----------------------------------------------
                    var docBodyObj = getNode('body', 'tagName') // eslint-disable-line
                    var scriptObj = createNode('script') // eslint-disable-line
                    setAttributes(scriptObj, {
                        id: 'kf-embed-lastUpdatedScript-' + config.profile,
                        type: 'text/javascript',
                        src: lastUpdatedUrl + config.profile,
                    })
                    appendChild(docBodyObj, scriptObj)

                    setStyles(info, { display: 'block' })

                    infoPaddingBorder =
                        /msie/i.test(navigator.userAgent) && !/opera/i.test(navigator.userAgent)
                            ? 0
                            : 12

                    setStyles(info, {
                        width:
                            getWidth(root) -
                            20 /* root padding */ -
                            (settings.borderStyle ? 2 : 0) /* root border */ -
                            infoPaddingBorder /* info padding-border */ +
                            'px',
                        top: getTop(foot) - 5 /* foot margin */ - getHeight(info) + 'px',
                        left: '10px' /* root padding */,
                    })
                }
            })

            // check if image did not load properly
            addEvent(img, 'error', function() {
                var error
                setStyles(img, { display: 'none' })
                setStyles(spinner, { display: 'none' })
                setStyles(info, { display: 'block' })

                error = createNode('div')
                setStyles(error, {
                    color: '#898989',
                    height: getHeight(info),
                })
                setHtml(error, 'Embedded visualization not available.')
                insertBefore(root, error, img)

                setStyles(info, { display: 'none' })
            })

            addEvent(img, 'load', function() {
                setStyles(img, { display: 'block' })
                setStyles(spinner, { display: 'none' })
            })
        }

        function getLastUpdated(profile, data) {
            var docBodyObj
            var scriptObj
            var lastUpdatedDate = data.lastUpdated
            var lastUpdatedObj = getNode('kf-embed-lastUpdated-' + profile, 'id')

            setHtml(lastUpdatedObj, 'Last updated: ' + lastUpdatedDate)

            // remove the script
            // -----------------
            docBodyObj = getNode('body', 'tagName')
            scriptObj = getNode('kf-embed-lastUpdatedScript-' + profile, 'id')
            removeChild(docBodyObj, scriptObj)
        }

        return {
            embedKlip: embedKlip,
            getLastUpdated: getLastUpdated,
        }
    })()
}
