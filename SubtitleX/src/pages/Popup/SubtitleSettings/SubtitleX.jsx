import React, { useEffect, useState } from 'react';
import { styled } from '@material-ui/core/styles';
import PublishIcon from '@material-ui/icons/Publish';
import Button from '@material-ui/core/Button';
import Grid from '@material-ui/core/Grid';
import Box from '@material-ui/core/Box';
import Container from '@material-ui/core/Container';
import Card from '@material-ui/core/Card'
import CardContent from '@material-ui/core/CardContent';
import Typography from '@material-ui/core/Typography';
import CardActions from '@material-ui/core/CardActions';

import { makeStyles } from '@material-ui/core/styles';
import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import FormHelperText from '@material-ui/core/FormHelperText';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import { fontSize, width } from '@material-ui/system';
import { getWantLangFromUserLang, remoteCall, fetchTextFromURL } from "../Common.jsx"

const useStyles = makeStyles((theme) => ({
    formControl: {
        minWidth: 120,
        fontSize: "16px",
        width: "100%"
    },
    selectEmpty: {
        marginTop: theme.spacing(2),
    },
    menuItem: {
        fontSize: "16px"
    }
}));

let seed = null;

export function getSeed(){
    return seed
}

const SubtitleX = () => {
    const classes = useStyles();
    //const [seed, setSeed] = useState({})
    const [subtitleId, setSubtitleId] = useState("");
    const [subtitleArray, setSubtitleArray] = useState([])
    const [listening, setListening] = useState(false)

    const handleSelectChange = (event) => {
        setSubtitleId(event.target.value);
    };
    const saveAndCheckStatusOfSeed = async (seed) => {
        const params = [
            seed.videoNo,
            seed.videoName,
            seed.m3u8Url,
            seed.pageUrl,
            seed.desc,
            seed.client,
        ];
        const result = await remoteCall("02ff8823-a0fd-420b-b39e-53b3a488365a", params);
        if (result && result.rc === "000") {
            seed = JSON.parse(result.data);
            return seed;
        } else {
            return null;
        }
    };
    const showSubtittle = async () => {
        console.log("subtitlex: showSubtitle "+subtitleId)
        //从server获取到文件
        if (subtitleId && subtitleId.length>0) {
            const sub_text = await fetchTextFromURL(subtitleId)
            const sub_blob = new Blob([sub_text], { type: "text/plain" });
            const sub_file = new File([sub_blob], "subtitle.srt", {
                type: "text/plain",
            });
            const eventFileUpload = new CustomEvent('fileUpload', { detail: sub_file });
            document.dispatchEvent(eventFileUpload);
        }
    }
    if (!listening) {
        setListening(true)
        //listen to the message of seed_detected
        window.addEventListener("message", async (event) => {
            console.log('subx subtitlex  received message ')
            if (
                event.source === window &&
                event.data.from === "subtitlex_injectScript" &&
                event.data.type === "seed_detected"
            ) {
                const pageUrl = event.data.seed.pageUrl;
                const s = await saveAndCheckStatusOfSeed(event.data.seed); //到后端获取seed信息
                if (s) {
                    s.url = pageUrl;
                    //显示subtitlex字幕信息
                    console.log("subtitlex: detected seed:")
                    console.log(s)
                    //setSeed(s)
                    seed = s
                    if (s && s.subtitle) {
                        setSubtitleArray(s.subtitle)
                    }
                    //用户选择字幕事件
                }
            }
        })
    }
    useEffect(() => {
        if (subtitleArray && subtitleArray.length > 0) {
            //自动选择用户浏览器语言
            const userLanguage = navigator.language || navigator.userLanguage;
            const userLangCode = getWantLangFromUserLang(userLanguage)
            console.log(subtitleArray)
            console.log('subtitlex: userLanguage = ' + userLangCode)
          
            for (var i = 0; i < subtitleArray.length; i++) {
                if (subtitleArray[i]["language"] == userLangCode) {
                    setSubtitleId(subtitleArray[i]["uuid"])
                    break
                }
            }
        }
    }, [subtitleArray])
    useEffect(() => {
        if (subtitleId) {
            console.log("subtitlex: subtitleId changed")
            console.log(subtitleId)
            showSubtittle()
        }

    }, [subtitleId])
    return (
        <Container className='subx-my-4'>
            <FormControl variant="outlined" className={classes.formControl}>
                <InputLabel id="subtitlex-language-select-outlined-label" style={{ fontSize: "16px", color:"rgb(32 228 255)" }}>SubtitleX</InputLabel>
                <Select
                    style={{ fontSize: "16px" }}
                    labelId="subtitlex-language-select-outlined-label"
                    id="subtitlex-language-select-outlined"
                    value={subtitleId}
                    onChange={handleSelectChange}
                    label="SubtitleX"
                >
                    {subtitleArray.map((sub, index) => {
                        return (
                        //   <MenuItem value="" className={classes.menuItem}>
                        //   <em>None</em>
                        //     </MenuItem>
                         <MenuItem key={sub["uuid"]} value={sub["uuid"]} className={classes.menuItem}>{sub["language"] + "-" + sub["subtitle_name"]}</MenuItem>
                        )
                    })}
                </Select>
            </FormControl>
        </Container>

    );
};

export default SubtitleX;
