window.isMobile = !1;
if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
    window.isMobile = !0
}
window.isiOS = !1;
if (/iPhone|iPad|iPod/i.test(navigator.userAgent)) {
    window.isiOS = !0
}
window.isiOSVersion = '';
if (window.isiOS) {
    var version = (navigator.appVersion).match(/OS (\d+)_(\d+)_?(\d+)?/);
    if (version !== null) {
        window.isiOSVersion = [parseInt(version[1], 10), parseInt(version[2], 10), parseInt(version[3] || 0, 10)]
    }
}
function t_throttle(fn, threshhold, scope) {
    var last;
    var deferTimer;
    threshhold || (threshhold = 250);
    return function() {
        var context = scope || this;
        var now = +new Date();
        var args = arguments;
        if (last && now < last + threshhold) {
            clearTimeout(deferTimer);
            deferTimer = setTimeout(function() {
                last = now;
                fn.apply(context, args)
            }, threshhold)
        } else {
            last = now;
            fn.apply(context, args)
        }
    }
}
function t702_initPopup(recId) {
    var rec = document.getElementById('rec' + recId);
    if (!rec)
        return;
    var container = rec.querySelector('.t702');
    if (!container)
        return;
    rec.setAttribute('data-animationappear', 'off');
    rec.setAttribute('data-popup-subscribe-inited', 'y');
    rec.style.opacity = 1;
    var documentBody = document.body;
    var popup = rec.querySelector('.t-popup');
    var popupTooltipHook = popup.getAttribute('data-tooltip-hook');
    var analitics = popup.getAttribute('data-track-popup');
    var popupCloseBtn = popup.querySelector('.t-popup__close');
    var hrefs = rec.querySelectorAll('a[href*="#"]');
    var submitHref = rec.querySelector('.t-submit[href*="#"]');
    if (popupTooltipHook) {
        t_onFuncLoad('t_popup__addAttributesForAccessibility', function() {
            t_popup__addAttributesForAccessibility(popupTooltipHook)
        });
        document.addEventListener('click', function(event) {
            var target = event.target;
            var href = target.closest('a[href$="' + popupTooltipHook + '"]') ? target : !1;
            if (!href)
                return;
            event.preventDefault();
            t702_showPopup(recId);
            t_onFuncLoad('t_popup__resizePopup', function() {
                t_popup__resizePopup(recId)
            });
            t702__lazyLoad();
            if (analitics && window.Tilda) {
                Tilda.sendEventToStatistics(analitics, popupTooltipHook)
            }
        });
        t_onFuncLoad('t_popup__addClassOnTriggerButton', function() {
            t_popup__addClassOnTriggerButton(document, popupTooltipHook)
        })
    }
    popup.addEventListener('scroll', t_throttle(function() {
        t702__lazyLoad()
    }));
    popup.addEventListener('click', function(event) {
        var windowWithoutScrollBar = window.innerWidth - 17;
        if (event.clientX > windowWithoutScrollBar)
            return;
        if (event.target === this)
            t702_closePopup(recId)
    });
    popupCloseBtn.addEventListener('click', function() {
        t702_closePopup(recId)
    });
    if (submitHref) {
        submitHref.addEventListener('click', function() {
            if (documentBody.classList.contains('t-body_scroll-locked')) {
                documentBody.classList.remove('t-body_scroll-locked')
            }
        })
    }
    for (var i = 0; i < hrefs.length; i++) {
        hrefs[i].addEventListener('click', function() {
            var url = this.getAttribute('href');
            if (!url || url.substring(0, 7) != '#price:') {
                t702_closePopup(recId);
                if (!url || url.substring(0, 7) == '#popup:') {
                    setTimeout(function() {
                        if (typeof t_triggerEvent === 'function')
                            t_triggerEvent(document.body, 'popupShowed');
                        documentBody.classList.add('t-body_popupshowed')
                    }, 300)
                }
            }
        })
    }
    function t702_escClosePopup(event) {
        if (event.key === 'Escape')
            t702_closePopup(recId)
    }
    popup.addEventListener('tildamodal:show' + popupTooltipHook, function() {
        document.addEventListener('keydown', t702_escClosePopup)
    });
    popup.addEventListener('tildamodal:close' + popupTooltipHook, function() {
        document.removeEventListener('keydown', t702_escClosePopup)
    });
    rec.addEventListener('conditional-form-init', function() {
        t_onFuncLoad('t_form__conditionals_addFieldsListeners', function() {
            t_form__conditionals_addFieldsListeners(recId, function() {
                t_popup__resizePopup(recId)
            })
        })
    }, {
        once: !0
    })
}
function t702_lockScroll() {
    var documentBody = document.body;
    if (!documentBody.classList.contains('t-body_scroll-locked')) {
        var bodyScrollTop = typeof window.pageYOffset !== 'undefined' ? window.pageYOffset : (document.documentElement || documentBody.parentNode || documentBody).scrollTop;
        documentBody.classList.add('t-body_scroll-locked');
        documentBody.style.top = '-' + bodyScrollTop + 'px';
        documentBody.setAttribute('data-popup-scrolltop', bodyScrollTop)
    }
}
function t702_unlockScroll() {
    var documentBody = document.body;
    if (documentBody.classList.contains('t-body_scroll-locked')) {
        var bodyScrollTop = documentBody.getAttribute('data-popup-scrolltop');
        documentBody.classList.remove('t-body_scroll-locked');
        documentBody.style.top = null;
        documentBody.removeAttribute('data-popup-scrolltop');
        document.documentElement.scrollTop = parseInt(bodyScrollTop)
    }
}
function t702_showPopup(recId) {
    var rec = document.getElementById('rec' + recId);
    if (!rec)
        return;
    var container = rec.querySelector('.t702');
    if (!container)
        return;
    var windowWidth = window.innerWidth;
    var screenMin = rec.getAttribute('data-screen-min');
    var screenMax = rec.getAttribute('data-screen-max');
    if (screenMin && windowWidth < parseInt(screenMin, 10))
        return;
    if (screenMax && windowWidth > parseInt(screenMax, 10))
        return;
    var popup = rec.querySelector('.t-popup');
    var popupTooltipHook = popup.getAttribute('data-tooltip-hook');
    var ranges = rec.querySelectorAll('.t-range');
    var documentBody = document.body;
    if (ranges.length) {
        Array.prototype.forEach.call(ranges, function(range) {
            t702__triggerEvent(range, 'popupOpened')
        })
    }
    t_onFuncLoad('t_popup__showPopup', function() {
        t_popup__showPopup(popup)
    });
    if (typeof t_triggerEvent === 'function')
        t_triggerEvent(document.body, 'popupShowed');
    documentBody.classList.add('t-body_popupshowed');
    documentBody.classList.add('t702__body_popupshowed');
    if (/iPhone|iPad|iPod/i.test(navigator.userAgent) && !window.MSStream && window.isiOSVersion && window.isiOSVersion[0] === 11) {
        setTimeout(function() {
            t702_lockScroll()
        }, 500)
    }
    t702__lazyLoad();
    t702__triggerEvent(popup, 'tildamodal:show' + popupTooltipHook);
    t_onFuncLoad('t_forms__calculateInputsWidth', function() {
        t_forms__calculateInputsWidth(recId)
    })
}
function t702_closePopup(recId) {
    var rec = document.getElementById('rec' + recId);
    var popup = rec.querySelector('.t-popup');
    var popupTooltipHook = popup.getAttribute('data-tooltip-hook');
    var popupAll = document.querySelectorAll('.t-popup_show:not(.t-feed__post-popup):not(.t945__popup)');
    if (popupAll.length == 1) {
        if (typeof t_triggerEvent === 'function')
            t_triggerEvent(document.body, 'popupHidden');
        document.body.classList.remove('t-body_popupshowed')
    } else {
        var newPopup = [];
        for (var i = 0; i < popupAll.length; i++) {
            if (popupAll[i].getAttribute('data-tooltip-hook') === popupTooltipHook) {
                popupAll[i].classList.remove('t-popup_show');
                newPopup.push(popupAll[i])
            }
        }
        if (newPopup.length === popupAll.length) {
            if (typeof t_triggerEvent === 'function')
                t_triggerEvent(document.body, 'popupHidden');
            document.body.classList.remove('t-body_popupshowed')
        }
    }
    if (typeof t_triggerEvent === 'function')
        t_triggerEvent(document.body, 'popupHidden');
    popup.classList.remove('t-popup_show');
    document.body.classList.remove('t702__body_popupshowed');
    if (/iPhone|iPad|iPod/i.test(navigator.userAgent) && !window.MSStream && window.isiOSVersion && window.isiOSVersion[0] === 11) {
        t702_unlockScroll()
    }
    t_onFuncLoad('t_popup__addFocusOnTriggerButton', function() {
        t_popup__addFocusOnTriggerButton()
    });
    setTimeout(function() {
        var popupHide = document.querySelectorAll('.t-popup:not(.t-popup_show)');
        for (var i = 0; i < popupHide.length; i++) {
            popupHide[i].style.display = 'none'
        }
    }, 300);
    t702__triggerEvent(popup, 'tildamodal:close' + popupTooltipHook)
}
function t702_sendPopupEventToStatistics(popupName) {
    var virtPage = '/tilda/popup/';
    var virtTitle = 'Popup: ';
    if (popupName.substring(0, 7) == '#popup:') {
        popupName = popupName.substring(7)
    }
    virtPage += popupName;
    virtTitle += popupName;
    if (window.Tilda && typeof Tilda.sendEventToStatistics == 'function') {
        Tilda.sendEventToStatistics(virtPage, virtTitle, '', 0)
    } else {
        if (ga) {
            if (window.mainTracker != 'tilda') {
                ga('send', {
                    hitType: 'pageview',
                    page: virtPage,
                    title: virtTitle
                })
            }
        }
        if (window.mainMetrika && window[window.mainMetrika]) {
            window[window.mainMetrika].hit(virtPage, {
                title: virtTitle,
                referer: window.location.href
            })
        }
    }
}
function t702_onSuccess(form) {
    t_onFuncLoad('t_forms__onSuccess', function() {
        t_forms__onSuccess(form)
    })
}
function t702__lazyLoad() {
    if (window.lazy === 'y' || document.getElementById('allrecords').getAttribute('data-tilda-lazy') === 'yes') {
        t_onFuncLoad('t_lazyload_update', function() {
            t_lazyload_update()
        })
    }
}
function t702__triggerEvent(el, eventName) {
    var event;
    if (typeof window.CustomEvent === 'function') {
        event = new CustomEvent(eventName)
    } else if (document.createEvent) {
        event = document.createEvent('HTMLEvents');
        event.initEvent(eventName, !0, !1)
    } else if (document.createEventObject) {
        event = document.createEventObject();
        event.eventType = eventName
    }
    event.eventName = eventName;
    if (el.dispatchEvent) {
        el.dispatchEvent(event)
    } else if (el.fireEvent) {
        el.fireEvent('on' + event.eventType, event)
    } else if (el[eventName]) {
        el[eventName]()
    } else if (el['on' + eventName]) {
        el['on' + eventName]()
    }
}
function t486_setHeight(recId) {
    var rec = document.getElementById('rec' + recId);
    if (!rec)
        return;
    var textWrapper = rec.querySelector('.t486__textwrapper');
    if (!textWrapper)
        return;
    var images = rec.querySelectorAll('.t486__blockimg');
    var imageContainer = rec.querySelector('.t486__imgcontainer');
    var imageHeight = images[0].clientWidth;
    if (window.innerWidth > 980) {
        for (var i = 0; i < images.length; i++) {
            images[i].style.height = imageHeight + 'px'
        }
        textWrapper.style.height = imageContainer.clientWidth + 'px'
    } else {
        var imageStyle = getComputedStyle(images[0], null);
        var imagePaddingLeft = parseInt(imageStyle.paddingLeft) || 0;
        var imagePaddingRight = parseInt(imageStyle.paddingRight) || 0;
        var imageWidth = images[0].clientWidth - (imagePaddingLeft + imagePaddingRight);
        for (var i = 0; i < images.length; i++) {
            images[i].style.height = imageWidth + 'px'
        }
        textWrapper.style.height = 'auto'
    }
}
function t846_init(recId) {
    t_onFuncLoad('t_card__moveClickOnCard', function() {
        t_card__moveClickOnCard(recId)
    });
    t_onFuncLoad('t_card__addFocusOnTab', function() {
        t_card__addFocusOnTab(recId)
    })
}
function t718_onSuccess(form) {
    form = form[0] ? form[0] : form;
    if (!form)
        return;
    if (form.tagName && form.tagName.toLowerCase() === 'input') {
        form = form.closest('.t-form')
    }
    var inputsWrapper = form.querySelector('.t-form__inputsbox');
    if (!inputsWrapper)
        return;
    var paddingTopInputs = parseInt(inputsWrapper.style.paddingTop, 10) || 0;
    var paddingBottomInputs = parseInt(inputsWrapper.style.paddingBottom, 10) || 0;
    var inputsHeight = inputsWrapper.clientHeight - (paddingTopInputs + paddingBottomInputs);
    var inputsOffset = inputsWrapper.getBoundingClientRect().top + window.pageYOffset;
    var inputsBottom = inputsHeight + inputsOffset;
    var targetOffset = form.querySelector('.t-form__successbox').getBoundingClientRect().top + window.pageYOffset;
    var target = null;
    if (window.innerWidth > 960) {
        target = targetOffset - 200
    } else {
        target = targetOffset - 100
    }
    var documentHeight = Math.max(document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight);
    if (targetOffset > window.pageYOffset || documentHeight - inputsBottom < window.innerHeight - 100) {
        inputsWrapper.classList.add('t718__inputsbox_hidden');
        var body = document.body;
        var paddingTopBody = parseInt(body.style.paddingTop, 10) || 0;
        var paddingBottomBody = parseInt(body.style.paddingBottom, 10) || 0;
        var bodyHeight = body.clientHeight - (paddingTopBody + paddingBottomBody);
        setTimeout(function() {
            if (window.innerHeight > bodyHeight) {
                setTimeout(function() {
                    var tildaLabel = document.querySelector('.t-tildalabel');
                    if (!tildaLabel)
                        return;
                    t718__fadeOut(tildaLabel)
                }, 50)
            }
        }, 300)
    } else {
        t718_scrollToTop(target);
        setTimeout(function() {
            inputsWrapper.classList.add('t718__inputsbox_hidden')
        }, 400)
    }
    var successUrl = form.getAttribute('data-success-url');
    if (successUrl) {
        setTimeout(function() {
            window.location.href = successUrl
        }, 500)
    }
}
function t718_scrollToTop(target) {
    if (target === window.pageYOffset) {
        return !1
    }
    var duration = 400;
    var difference = window.pageYOffset;
    var cashedDiff = window.pageYOffset;
    var step = (Math.abs(window.pageYOffset - target) * 10) / duration;
    var scrollInterval = setInterval(function() {
        if (cashedDiff > target) {
            difference -= step
        } else {
            difference += step
        }
        window.scrollTo(0, difference);
        document.body.setAttribute('data-scrollable', 'true');
        if (cashedDiff > target && window.pageYOffset <= target) {
            document.body.removeAttribute('data-scrollable');
            clearInterval(scrollInterval)
        } else if (cashedDiff <= target && window.pageYOffset >= target) {
            document.body.removeAttribute('data-scrollable');
            window.scrollTo(0, target);
            clearInterval(scrollInterval)
        }
    }, 10);
    var scrollTimeout = setTimeout(function() {
        clearInterval(scrollInterval);
        document.body.removeAttribute('data-scrollable');
        clearTimeout(scrollTimeout)
    }, duration * 2)
}
function t718__fadeOut(element) {
    if (element.style.display === 'none')
        return;
    var opacity = 1;
    var timer = setInterval(function() {
        element.style.opacity = opacity;
        opacity -= 0.1;
        if (opacity <= 0.1) {
            clearInterval(timer);
            element.style.display = 'none';
            element.style.opacity = null
        }
    }, 50)
}
function t389_scrollToTop() {
    var duration = 700;
    var difference = window.pageYOffset;
    var step = 10 * difference / duration;
    var timer = setInterval(function() {
        difference -= step;
        window.scrollTo(0, difference);
        document.body.setAttribute('data-scrollable', 'true');
        if (window.pageYOffset === 0) {
            document.body.removeAttribute('data-scrollable');
            clearInterval(timer)
        }
    }, 10)
}
function t454_setLogoPadding(recid) {
    var rec = document.getElementById('rec' + recid);
    if (!rec || window.innerWidth <= 980)
        return;
    var menu = rec.querySelector('.t454');
    var logo = menu ? menu.querySelector('.t454__logowrapper') : null;
    var leftWrapper = menu ? menu.querySelector('.t454__leftwrapper') : null;
    var rightWrapper = menu ? menu.querySelector('.t454__rightwrapper') : null;
    var logoWidth = logo ? logo.offsetWidth : 0;
    var updateWidth = (logoWidth / 2) + 50;
    if (leftWrapper)
        leftWrapper.style.paddingRight = updateWidth + 'px';
    if (rightWrapper)
        rightWrapper.style.paddingLeft = updateWidth + 'px'
}
