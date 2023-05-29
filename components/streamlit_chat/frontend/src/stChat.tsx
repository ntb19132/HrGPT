import {
  // eslint-disable-next-line 
  Streamlit,
  StreamlitComponentBase,
  withStreamlitConnection,
} from "streamlit-component-lib"
import React, { ReactNode } from "react"
import styled from '@emotion/styled'
import { css } from '@emotion/react'
import { FaThumbsUp,FaThumbsDown } from "react-icons/fa";


class Chat extends StreamlitComponentBase {
  handleFeedback = (value:string) => {
    // Call the onClick callback function for "like" button
    Streamlit.setComponentValue(value)
  };
  public render = (): ReactNode => {
    Streamlit.setFrameHeight(window.innerHeight)
    const { isUser, avatarStyle, seed, message, logo } = this.props.args;
    const avatarUrl = !!logo ? logo: `https://api.dicebear.com/5.x/${avatarStyle}/svg?seed=${seed}`
    
    // Streamlit sends us a theme object via props that we can use to ensure
    // that our component has visuals that match the active theme in a
    // streamlit app.
    const { theme } = this.props
    
    // Maintain compatibility with older versions of Streamlit that don't send
    // a theme object.
    if (!theme) {
      return <div>Theme is undefined, please check streamlit version.</div>
    }
    
    // styles for the avatar image
    const Avatar = styled.img({
      border: `1px solid transparent`,
      borderRadius: '50%',
      height: '3rem',
      width: '3rem',
      margin: 0
    })
    
    // styles for the message box
    const Message = styled.div({
      display: 'inline-block',
      background: theme.secondaryBackgroundColor,
      border: '1px solid transparent',
      borderRadius: '10px',
      padding: '10px 14px',
      margin: '5px 20px',
      maxWidth: '70%',
      whiteSpace: 'pre-line'
    })
    const ButtonContainer = styled.div({
      display: "flex",
      justifyContent: "flex-end",
      marginTop: "10px",
      textAlign: "center",
      outline: "none"
    });

    const Button = styled.button({
      width: "2rem",
      height: "2rem",
      marginLeft: "10px",
      borderRadius: "50%",
      border: "none",
      cursor: "pointer",
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      // transition: "background-color 0.3s ease",
      background: theme.secondaryBackgroundColor,
      outline: "none",
      textAlign: "center",
      ":active": {
        backgroundColor: theme.primaryColor,
      },
    });
    
    // styles for the container
    const Chat = styled.div({
      display: 'flex',
      // flexDirection: 'row',
      fontFamily: `${theme.font}, 'Segoe UI', 'Roboto', sans-serif`, 
      height: 'auto',
      margin: 0,
      width: '100%'
    }, 
    (props: {isUser: boolean}) => {  // specific styles
      if (props.isUser){
        return css`
          flex-direction: row-reverse;
          & > div {
            text-align: right;
          }
        `
      }
      return css``
    })

    return (
      <Chat isUser={isUser}>
        <Avatar src={avatarUrl} alt="profile" draggable="false"/>
        <Message>{message}</Message>
        {!isUser && (
            <ButtonContainer>
              <Button onClick={() => this.handleFeedback('like')}><FaThumbsUp color={theme.textColor}></FaThumbsUp></Button>
              <Button onClick={() => this.handleFeedback('dislike')}><FaThumbsDown color={theme.textColor}></FaThumbsDown></Button>
            </ButtonContainer>
        )}
      </Chat>
    )
  }
}

export default withStreamlitConnection(Chat);
